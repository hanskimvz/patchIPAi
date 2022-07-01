<?
$fname = "/mnt/plugin/crpt/crpt.ini";
$config = parse_ini_file($fname);
// print_r($config);

if (!isset($config['crpt.enable']) || 
    !isset($config['table0.enable']) || 
    !isset($config['table0.interval']) || 
    !isset($config['table0.rollovercount']) || 
    !isset($config['table1.enable']) || 
    !isset($config['table1.interval']) || 
    !isset($config['table1.rollovercount']) || 
    !isset($config['table2.enable']) || 
    !isset($config['table2.interval']) || 
    !isset($config['table2.rollovercount']) || 
    !isset($config['table3.enable']) || 
    !isset($config['table3.interval']) || 
    !isset($config['table3.rollovercount'])) {

	print "Not Valid config file\n";
	exit();
}
if(!$config['crpt.enable']) {
    print "CRPT not ENABLED";
    exit();
}

function getCurCounting() {
    $arr_rs = array();
    $filename = "/mnt/plugin/.config/vca-cored/configuration/api.json";
    $json_body = file_get_contents($filename);
    $arr = json_decode($json_body, true)['observables'];
	// print_r($arr);
	foreach($arr as $n=>$vca){
		if ($vca['typename'] == 'vca.observable.Counter') {
			array_push($arr_rs, ["idx"=>$n, "name"=>$vca['name'], "value"=>$vca['count']]);	
		}
	}
    return $arr_rs;   
}

function putCounting($datetime, $filedb, $arr_count, $max_roll_over_count){
    $db_body = file_get_contents($filedb);
    $arr_rs = json_decode($db_body, true);
    if(!$arr_rs) {
        $arr_rs = array();
    }
    array_push($arr_rs, ["datetime"=>$datetime, "counters"=>$arr_count]);
    if (sizeof($arr_rs) > $max_roll_over_count){
        array_shift($arr_rs);
    }
    $json_body = json_encode($arr_rs);
    file_put_contents($filedb, $json_body);
}


$filedb0 = "/mnt/plugin/.config/vca-cored/configuration/countreport.table0.db";
$filedb1 = "/mnt/plugin/.config/vca-cored/configuration/countreport.table1.db";
$filedb2 = "/mnt/plugin/.config/vca-cored/configuration/countreport.table2.db";
$filedb3 = "/mnt/plugin/.config/vca-cored/configuration/countreport.table3.db";

for ($i=0; $i<4; $i++) {
    if (!file_exists(${'filedb'.$i})) {
        file_put_contents(${'filedb'.$i},"");
    }
}
require('/root/web/cgi-bin/_define.inc');
require('/root/web/cgi-bin/class/system.class');
$shm_id = shmop_open(KEY_SM_SHARED_CONFIG, "a", 0, 0);
$system_conf = new CSystemConfiguration($shm_id);
shmop_close($shm_id);
$TimezoneIndex = $system_conf->SystemDatetime->TimeZoneIndex;
$timezone = "Etc/GMT".($TimezoneIndex-12 >0 ? "-".strval($TimezoneIndex-12): "+".strval(12-$TimezoneIndex));
date_default_timezone_set($timezone);

$ts = time();
$arrCount = getCurCounting();

if (!$arrCount) {
    exit();
}
// print_r($arrCount);
for ($i=0; $i<4; $i++){
    if ($config['table'.$i.'.enable']) {
        $t_flag = ($ts+2)%$config['table'.$i.'.interval'];

        if($t_flag <10){
            $timestamp = floor($ts/$config['table'.$i.'.interval']) * $config['table'.$i.'.interval'];
            $datetime =  date("Y/m/d H:i:s", $timestamp);
            putCounting($datetime, ${'filedb'.$i}, $arrCount, $config['table'.$i.'.rollovercount']);
        }
    }
}

exit();

?>