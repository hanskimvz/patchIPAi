<?
$fname_crpt = "/mnt/plugin/crpt/crpt.ini";
$fname_tlss = "/mnt/plugin/crpt/tlss.ini";
if (!file_exists($fname_crpt)) {
    $body = "".
    "crpt.enable = yes\n".
    "table0.enable = yes\n".
    "table0.interval = 60\n".
    "table0.rollovercount = 10080\n".
    "table1.enable = yes\n".
    "table1.interval = 600\n".
    "table1.rollovercount = 8640\n".
    "table2.enable = no\n".
    "table2.interval = 3600\n".
    "table2.rollovercount = 2880\n".
    "table3.enable = no\n".
    "table3.interval = 86400\n".
    "table3.rollovercount = 365\n";
    
    file_put_contents($fname_crpt, "");
    print "No CRPT config file".PHP_EOL;
    exit();
}
if (!file_exists($fname_tlss)) {
    print "No TLSS config file".PHP_EOL;
    exit();
}

$config['crpt'] = parse_ini_file($fname_crpt);
$config['tlss'] = parse_ini_file($fname_tlss);

if (!isset($config['crpt']['crpt.enable']) || 
    !isset($config['crpt']['table0.enable']) || 
    !isset($config['crpt']['table0.interval']) || 
    !isset($config['crpt']['table0.rollovercount']) || 
    !isset($config['crpt']['table1.enable']) || 
    !isset($config['crpt']['table1.interval']) || 
    !isset($config['crpt']['table1.rollovercount']) || 
    !isset($config['crpt']['table2.enable']) || 
    !isset($config['crpt']['table2.interval']) || 
    !isset($config['crpt']['table2.rollovercount']) || 
    !isset($config['crpt']['table3.enable']) || 
    !isset($config['crpt']['table3.interval']) || 
    !isset($config['crpt']['table3.rollovercount'])) {

	print "Not Valid CRPT config file\n";
	exit();
}
if (!isset($config['tlss']['enable']) || 
    !isset($config['tlss']['IP']) || 
    !isset($config['tlss']['PORT']) || 
    !isset($config['tlss']['INTERVAL']) ) {
	
    print "Not Valid HOSTED SERVICE config file\n";
	exit();
}

if (isset($_GET['act']) && $_GET['act'] == 'query_setting'){
    $json_str = json_encode($config);
    print $json_str;
    exit();
}
else if (isset($_GET['act']) && $_GET['act'] == 'modify_setting'){
    print "modify setting";
    // print_r($_GET);
    if(isset($_GET['crpt_enable'])) {
        if($_GET['crpt_enable']=='true') {
            $config['crpt']['crpt.enable'] = 'yes';
            for($i=0; $i<4; $i++){
                if( $_GET['table'][$i]['enable']=='true') {
                    $config['crpt']['table'.$i.'.enable'] = 'yes';
                    $config['crpt']['table'.$i.'.interval'] = $_GET['table'][$i]['sampling_interval']*60;
                    $config['crpt']['table'.$i.'.rollovercount'] = $_GET['table'][$i]['roll_count'];
                }
                else {
                    $config['crpt']['table'.$i.'.enable'] = 'no';
                }
            }
        }
        else {
            $config['crpt']['crpt.enable'] = 'no';
        }
        // print_r($config['crpt']);
        put_ini_file($fname_crpt, $config['crpt']);
        print "OK";
    }
    else if(isset($_GET['tlss_enable'])) {
        if($_GET['tlss_enable']=='true') {
            $config['tlss']['enable'] = 'yes';
            $config['tlss']['IP'] = $_GET['tlss_server_address'];
            $config['tlss']['PORT'] = $_GET['tlss_server_port'];
            $config['tlss']['INTERVAL'] = $_GET['tlss_update_interval']*60;
        }
        else {
            $config['tlss']['enable'] = 'no';
        }
        // print_r($config['tlss']);
        put_ini_file($fname_tlss,$config['tlss']);
        print "OK";

    }
    exit();

}

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

// require('/root/web/cgi-bin/_define.inc');
// require('/root/web/cgi-bin/class/system.class');
// $shm_id = shmop_open(KEY_SM_SHARED_CONFIG, "a", 0, 0);
// $system_conf = new CSystemConfiguration($shm_id);
// shmop_close($shm_id);
// $TimezoneIndex = $system_conf->SystemDatetime->TimeZoneIndex;
// $timezone = "Etc/GMT".($TimezoneIndex-12 >0 ? "-".strval($TimezoneIndex-12): "+".strval(12-$TimezoneIndex));
// date_default_timezone_set($timezone);

?>

<!DOCTYPE html>
<html class="setup_html">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=10" /> 
    <title>Administrator Tool</title>
    <link rel="stylesheet" href="/css/dom.css" type="text/css" />	
    <link rel="stylesheet" href="/css/admin.css" type="text/css"/>
</head>
<!--body onload="onLoadPage();" oncontextmenu="return false" onselectstart="return false"  ondragstart="return false"-->
<body onload="onLoadPage();">
    <div class="contentTitle"><span tkey="crpt_tlss_configuration">Counting Report & Hosted Service</span></div>
		<div class="content">
			<label class="maintitle"><span tkey="counting_report">Counting Report Service</span></label>
			<input id="crpt_disable" type="radio" name="crpt_enable" value=0 >
			<label for="crpt_disable"></label><span tkey=off>Off</span>
			<input id="crpt_enable" type="radio"  name="crpt_enable" value=1 >
			<label for="crpt_enable"></label><span tkey=on>On</span><br>
            <label></label><br/>


<? for ($i=0; $i<4; $i++) { ?>
    <br/>
            <label class="maintitle">
                <input id="crpt_table<?=$i?>_enable" type="checkbox" name="crpt_table<?=$i?>_enable">
                <label for="crpt_table<?=$i?>_enable"></label>
                <span tkey="crpt_table<?=$i?>">Table<?=$i?></span></label>

            <label class="subtitle"><span tkey="sampling_interval">Sampling Interval</span></label>
			<input type="text" id="table<?=$i?>_sampling_interval" maxlength="20" /><span tkey="minute">Minutes</span><br />
            <label class="subtitle"><span tkey="roll_over_count">Roll-over Count</span></label>
            <input type="text" id="table<?=$i?>_roll_count" maxlength="20"/><br />
            <label class="subtitle"><span tkey="max_roll_over_count">Max Roll-over Time</span></label>
            <input type="text" id="table<?=$i?>_max_roll_count" maxlength="20" readonly/><br />
            <label></label>
<?}?>
		</div>
        <center><button id="btCRPTOK" class="button" onclick="putSetting(this)"><span tkey="apply">APPLY</span></button></center> 
        <br />
        <div class="content">
			<label class="maintitle"><span tkey="Hosted_service">Hosted Service</span></label>
			<input id="tlss_disable" type="radio" name="tlss_enable" value=0 >
			<label for="tlss_disable"></label><span tkey=off>Off</span>
			<input id="tlss_enable" type="radio"  name="tlss_enable" value=1 >
			<label for="tlss_enable"></label><span tkey=on>On</span><br>
            <label></label>

            <label class="subtitle"><span tkey="tlss_server_address">Server address</span></label>
			<input type="text" id="tlss_server_address" maxlength="20" /><br />
            <label class="subtitle"><span tkey="tlss_server_port">Server port</span></label>
            <input type="text" id="tlss_server_port" maxlength="20" /><br />
            <label class="subtitle"><span tkey="update_interval">Update interval</span></label>
            <input type="text" id="tlss_update_interval" maxlength="20" /><span tkey="minute">Minutes</span><br />
        </div>
		<center><button id="btTLSSOK" class="button" onclick="putSetting(this)"><span tkey="apply">APPLY</span></button></center> 
	</body>
</html>
<script src="/js/jquery1.11.1.min.js"></script>
<script>

function getSetting(){
    url = "./setup_operator.cgi?act=query_setting";
    console.log(url);

    $.getJSON(url, function(response) {
        console.log(response);
        document.getElementById("crpt_disable").checked= response['crpt']['crpt.enable'] ? false: true;
        document.getElementById("crpt_enable").checked= response['crpt']['crpt.enable'] ? true : false;
        for (i=0; i<4; i++){
            document.getElementById("crpt_table"+i+"_enable").checked= response['crpt']['table'+i+'.enable'] ? true : false;
            document.getElementById("table"+i+"_sampling_interval").value = response['crpt']['table'+i+'.interval']/60;
            document.getElementById("table"+i+"_roll_count").value = response['crpt']['table'+i+'.rollovercount'];
            
            max_roll_secs = response['crpt']['table'+i+'.rollovercount']*response['crpt']['table'+i+'.interval'];
            if (max_roll_secs<=3600*24) {
                max_roll_over_count = max_roll_secs/3600 + " hours";
            }
            else if (max_roll_secs > 3600*24) {
                max_roll_over_count = max_roll_secs/3600/24 + " days";
            }
            document.getElementById("table"+i+"_max_roll_count").value = max_roll_over_count;
        }
        document.getElementById("tlss_disable").checked= response['tlss']['enable'] ? false: true;
        document.getElementById("tlss_enable").checked= response['tlss']['enable'] ? true : false;
        document.getElementById("tlss_server_address").value = response['tlss']['IP'];
        document.getElementById("tlss_server_port").value = response['tlss']['PORT'];
        document.getElementById("tlss_update_interval").value = response['tlss']['INTERVAL']/60;
    });
}    
function checkValue(xid){
    console.log(xid);
    if (xid == 'btCRPTOK' && document.getElementById("crpt_enable").checked){
        for (i=0; i<4; i++) {
            if (document.getElementById("crpt_table"+i+"_enable").checked) {
                val = document.getElementById("table"+i+"_sampling_interval").value;
                if (!val || isNaN(val) || val<=0 ) {
                    alert("table"+i+"_sampling_interval", val, "Fail");
                    return false;
                }
                val = document.getElementById("table"+i+"_roll_count").value;
                if (!val || isNaN(val) || val<=0 ) {
                    alert("table"+i+"_sampling_interval", val, "Fail");
                    return false;
                }
            }
        }
    }
    else if (xid == 'btTLSSOK' && document.getElementById("tlss_enable").checked){
        val = document.getElementById("tlss_server_address").value;
        m_ip = val.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/);
        if (!m_ip) {
            alert("wrong IP");
            return false;
        }
        m_ip.forEach((n, idx)=>{
            console.log(n, idx);
            if (idx && (n<0 || n>255)) {
                alert("wrong IP");
                return false;
            }
            
        });

        val = document.getElementById("tlss_server_port").value;
        if (!val || isNaN(val) || val<=0 ) {
            alert("tlss_server_port" + val+ ": Fail");
            return false;
        }
        val = document.getElementById("tlss_update_interval").value;
        if (!val || isNaN(val) || val<=0 ) {
            alert("tlss_update_interval", val, "Fail");
            return false;
        }
    }
    return true;
}
function putSetting(t){
    flag = checkValue(t.id);
    if (!flag) {
        return false;
    }
    url = './setup_operator.cgi'
    if (t.id == 'btCRPTOK'){
        data ={
            crpt_enable: document.getElementById("crpt_enable").checked,
            table: []
        };
        
        for(i=0; i<4; i++){
            data['table'].push({
                enable: document.getElementById("crpt_table"+i+"_enable").checked,
                sampling_interval: document.getElementById("table"+i+"_sampling_interval").value,
                roll_count: document.getElementById("table"+i+"_roll_count").value
            });
        }
        
    }
    else if (t.id == 'btTLSSOK'){
        data ={
            tlss_enable: document.getElementById("tlss_enable").checked,
            tlss_server_address: document.getElementById("tlss_server_address").value,
            tlss_server_port: document.getElementById("tlss_server_port").value,
            tlss_update_interval: document.getElementById("tlss_update_interval").value
        }
    }
    else {
        return false;
    }
    $.ajax({
        type:"get",
        url: url + '?act=modify_setting',
        data: data,	
        success: function(msg){
            console.log(msg);
            var response = msg.trim();
        },
        error: function() {
        }	
	});    

}
function onLoadPage() {
    getSetting();
    console.log('HELLO');
}    
</script>


