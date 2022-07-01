#!/usr/bin/php-cgi -q
<?
$fname = "/mnt/plugin/crpt/tlss.ini";
function put_ini_file($file, $array, $i = 0){
    $str = "";
    foreach ($array as $k => $v) {
        if (is_array($v)) {
            $str .= str_repeat(" ", $i * 2) . "[{$k}]" . PHP_EOL;
            $str .= put_ini_file("", $v, $i + 1);
        } 
		else {
            $str .= str_repeat(" ", $i * 2) . "{$k} = {$v}" . PHP_EOL;
        }
    }
    if ($file) {
        return file_put_contents($file, $str);
    } 
	else {
        return $str;
    }
}


if (!is_file($fname)) {
	print "No config file";
	exit();
}


$config = parse_ini_file($fname);

if (!isset($config['enable']) 	|| !$config['enable'] ||
	!isset($config['IP']) 	 	|| !$config['IP'] ||
	!isset($config['PORT']) 	|| !$config['PORT'] ||
	!isset($config['INTERVAL']) || !$config['INTERVAL'] ) {

	print "Not Valid config file\n";
	exit();
}

if (!$config['enable']) {
	print "Service disabled";
	exit();
}

if (!isset($config['last_access'])) {
	$config['last_access'] = time();
}

if (time() - $config['last_access'] < $config['INTERVAL']) {
	print "exit due to less time ".(time() - $config['last_access'])."\n";
	exit();
}

exec('/usr/bin/php-cgi -q /mnt/plugin/crpt/param.cgi "group=basic"', $rs);
$device_info = trim(implode($rs));

function dot_flatten($input_arr, $return_arr = array(), $prev_key = '') {
	foreach ($input_arr as $key => $value)	{
	   $new_key = $prev_key . $key;
	   // check if it's associative array 99% good
	   if (is_array($value) && key($value) !==0 && key($value) !==null)	   {
		   $return_arr = array_merge($return_arr, dot_flatten($value, $return_arr, $new_key . '.'));
	   }
	   else  {
		   $return_arr[$new_key] = $value;
	   }
   }
   return $return_arr;
}

function send_tlss_message($sock, $mesg='') {
	$length = strlen($mesg);
	$s_num = pack("CCCC", $length&0xFF, ($length>>8)&0xFF, ($length>>16)&0xFF, ($length>>24)&0xFF);
	// socket_send($sock, $s_num, 4, 0);
	// socket_write($sock, $mesg);
	$rs = sprintf("send_message: s_num:%d, %s", $length, $mesg);
	try {
		socket_send($sock, $s_num, 4, 0);
		socket_write($sock, $mesg);
	}
	catch(Exception $e){
		return  "\n".$e->getMessage();
	}
	return $rs;
}

function recv_tlss_message($sock){
	$num = 0;
	$bytes = socket_recv($sock, $recv, 4, 0); 
	try {
		$num = ord($recv[0]) + (ord($recv[1])<<8) + (ord($recv[2])<<16) + (ord($recv[3])<<24);
	}
	catch(Exception $e){
		return  "\n".$e->getMessage();
	}
	$recv = socket_read($sock, intval($num)); 
	printf("\n r_num:%d, bytes:%d, ,mesg:%s", $num, $bytes, $recv);
	return $recv;
}


function TLSS_CLIENT($IP, $PORT) {
	global $device_info;
	$sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP); 
	socket_set_option($sock, SOL_SOCKET, SO_RCVTIMEO, array('sec' => 5, 'usec' => 0));
	socket_set_option($sock, SOL_SOCKET, SO_SNDTIMEO, array('sec' => 5, 'usec' => 0));

	$conn = socket_connect($sock, $IP, $PORT); 
	if (!$conn) {
		print ("SOCKET TIMEOUT\n");
		socket_close($sock); 
		return False;
	}
	echo "\nCLIENT >> socket connect to ".$IP.":".$PORT; 

	print ("\n");
	print(send_tlss_message($sock, $device_info));

	for ($i=0; $i<10; $i++) {
		$recv = recv_tlss_message($sock);
		if ($recv == "done\n" || $recv == "done\0") {
			socket_close($sock); 
			echo "CLIENT >> socket closed.\n"; 
			return True;			
		}
		$ex = explode("?", $recv);
		if (strpos($ex[0], "param.fcgi") || strpos($ex[0], "param.cgi") || strpos($ex[0], "api.json")) {
			if(strpos($ex[0], "api.json")) {
				$ex[1] = "group=vca";
			}
			$out = array();
			exec('/usr/bin/php-cgi -q /mnt/plugin/crpt/param.cgi "'.$ex[1].'"', $out);
			$contents = trim(implode(PHP_EOL, $out));
		}
		else if (strpos($ex[0], "snapshot.cgi") || strpos($ex[0], "video.cgi") ) {
			system('/usr/bin/php-cgi -q /root/web/'.$ex[0].' "'.$ex[1].'" > /tmp/out');
			$contents = file_get_contents('/tmp/out');		

		}
		else {
			// $outfile = "out";
			// system('/usr/bin/php-cgi -q /root/web/'.$ex[0].' "'.$ex[1].'" > '.$outfile);
			// $contents = file_get_contents($outfile);

			$out = array();
			exec('/usr/bin/php-cgi -q /root/web/'.$ex[0].' "'.$ex[1].'"', $out);
			$contents = implode(PHP_EOL, $out);
		}
		$st = send_tlss_message($sock, $contents);
		// print("\n".substr($st,0,300));
		
	}
	socket_close($sock); 
	echo "CLIENT >> socket closed.\n"; 
	
	return True;
}



$x = TLSS_CLIENT($config['IP'], $config['PORT']);
if($x) {
	$config['last_access'] = time();
	print "last access update to ".$config['last_access'].": ".date("Y-m-d H:i:s", $config['last_access']);
	print PHP_EOL;
	put_ini_file($fname, $config);
}
exit();
// php-cgi /root/web/cgi-bin/operator/countreport.cgi "reportfmt=table&to=now&counter=active&sampling=60&order=ascending&value=diff&from=2022-03-09" > 1.txt

// function dummyArr2Dot($arr){
// 	$n=0;
// 	foreach($arr as $A=>$B){
// 		if (!is_array($B)) {
// 			$line[$n] = $A."=".$B;
// 			$n++;
// 		}
// 		else {
// 			foreach($B as $C=>$D){
// 				if (!is_array($D)) {
// 					$line[$n] =  $A.".".$C."=".$D;
// 					$n++;
// 				}
// 				else {
// 					foreach($D as $E=>$F){
// 						if (!is_array($F)) {
// 							$line[$n] = $A.".".$C.".".$E."=".$F;
// 							$n++;
// 						}
// 						else {
// 							foreach($F as $G=>$H){
// 								if (!is_array($H)) {
// 									$line[$n] = $A.".".$C.".".$E.".".$G."=".$H;
// 									$n++;
// 								}
// 								else {
// 									foreach($H as $I=>$J){
// 										if (!is_array($J)) {
// 											$line[$n] = $A.".".$C.".".$E.".".$G.".".$I."=".$J;
// 											$n++;
// 										}
// 										else {
// 											foreach($J as $K=>$L){
// 												if (!is_array($L)) {
// 													$line[$n] = $A.".".$C.".".$E.".".$G.".".$I.".".$K."=".$L;
// 													$n++;
// 												}
// 												else {
// 													foreach($L as $M=>$N){
// 														if (!is_array($N)) {
// 															$line[$n] = $A.".".$C.".".$E.".".$G.".".$I.".".$K.".".$M."=".$N;
// 															$n++;
// 														}
// 														else {
// 															$line[$n] = $A.".".$C.".".$E.".".$G.".".$I.".".$K.".".$M."=".$N;
// 															$n++;
// 														}
// 													}
// 												}
// 											}		
// 										}
// 									}		
// 								}
// 							}
			
// 						}
// 					}
// 				}
// 			}
// 		}
// 	}
// 	foreach($line as $line){
// 		$body .= $line."\n";
// 	}
// 	return $body;
// }
// function arr2dotArgument($array,$n=0){
// 	$str = "";
// 	$p =  "";
//     foreach ($array as $k => $v) {
//         if (is_array($v)) {
//             $str .= $k . ".";
// 			$p .= $k.".";
//             $str .= arr2dotArgument($v, $n+1);
//         } 
// 		else {
//             // $str .= $k." = ".$v. PHP_EOL;
// 			$str .= $p.$k." = ".$v. PHP_EOL;
// 			// $n++;
//         }
//     }
//     return $str;
// }

// $body = file_get_contents("/mnt/plugin/.config/vca-cored/configuration/api.json");
// $arr = json_decode($body, true);
// $contents = arr2dotArgument($arr);

// print_r($contents);

?>