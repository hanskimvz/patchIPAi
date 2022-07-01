<?
$fname_tlss = "/mnt/plugin/patch/tlss.ini";
if (!file_exists($fname_tlss)) {
    print "No TLSS config file".PHP_EOL;
    exit();
}

$config = parse_ini_file($fname_tlss);
if (!isset($config['enable']) || 
    !isset($config['IP']) || 
    !isset($config['PORT']) || 
    !isset($config['INTERVAL']) ) {
	
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
    if(isset($_GET['tlss_enable'])) {
        if($_GET['tlss_enable'] == 'true') {
            $config['enable'] = 'yes';
            $config['IP'] = $_GET['tlss_server_address'];
            $config['PORT'] = $_GET['tlss_server_port'];
            $config['INTERVAL'] = $_GET['tlss_update_interval']*60;
        }
        else {
            $config['enable'] = 'no';
        }
        // print_r($config);
        put_ini_file($fname_tlss, $config);
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

?>

<!-- <!DOCTYPE html>
<html class="setup_html">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=10" /> 
    <title>Administrator Tool</title>
    <link rel="stylesheet" href="/css/dom.css" type="text/css" />	
    <link rel="stylesheet" href="/css/admin.css" type="text/css"/>
</head> -->
<!--body onload="onLoadPage();" oncontextmenu="return false" onselectstart="return false"  ondragstart="return false"-->
<body onload="onLoadPage();">
    <div class="contentTitle"><span tkey="tlss_configuration">Hosted Service Configuration</span></div>
        <div class="content">
			<label class="maintitle"><span tkey="hosted_service">Hosted Service</span></label>
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
<!-- </html> -->
<script>
function getSetting(){
    url = "./vca/hosted_service/setup_vca_hosted_service.cgi?act=query_setting";
    console.log(url);

    $.getJSON(url, function(response) {
        console.log(response);
        document.getElementById("tlss_disable").checked= response['enable'] ? false: true;
        document.getElementById("tlss_enable").checked= response['enable'] ? true : false;
        document.getElementById("tlss_server_address").value = response['IP'];
        document.getElementById("tlss_server_port").value = response['PORT'];
        document.getElementById("tlss_update_interval").value = response['INTERVAL']/60;
    });
}    
function checkValue(xid){
    console.log(xid);
    if (xid == 'btTLSSOK' && document.getElementById("tlss_enable").checked){
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
            alert("tlss_server_port" + val + ": Fail");
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
    url = './vca/hosted_service/setup_vca_hosted_service.cgi';
    if (t.id == 'btTLSSOK'){
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

getSetting();
</script>


