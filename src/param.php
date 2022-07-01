<?
$_DOC_ROOT= '/root/web';
require($_DOC_ROOT.'/cgi-bin/_define.inc');
require($_DOC_ROOT.'/cgi-bin/class/system.class');
require($_DOC_ROOT.'/cgi-bin/class/network.class');
$system_conf = new CSystemConfiguration();
$net_conf = new CNetworkConfiguration();

function dot_flatten($arr, $narr = array(), $nkey = '') {
    foreach ($arr as $key => $value) {
        if (is_array($value)) {
            $narr = array_merge($narr, dot_flatten($value, $narr, $nkey . $key . '.'));
        } else {
            $narr[$nkey . $key] = $value;
        }
    }

    return $narr;
}

if (!isset($_GET['group'])) {
    $_GET['group'] = 'all';
}
if (!isset($_GET['action'])) {
    $_GET['action'] = 'list';
}

if ($_GET['group'] == 'basic') {
    $model = trim($GLOBALS['system_conf']->DeviceInfo->Model);
    $brand = trim($GLOBALS['system_conf']->DeviceInfo->Manufacturer);
    $mac = trim($GLOBALS['net_conf']->HwAddress);
    $device_info = sprintf("mac=%s&brand=%s&model=%s", str_replace(":", "", $mac), $brand, $model);
    print $device_info;
    exit();
}


$arr = array();

if ($_GET['group'] == 'all') {
	$arr['BRAND.brand'] = $system_conf->DeviceInfo->Manufacturer;
	$arr['BRAND.authenkey'] = $system_conf->DeviceInfo->Token;
	$arr['BRAND.Product.fullname'] = $system_conf->DeviceInfo->Model;
	$arr['BRAND.Product.shortname'] = $system_conf->DeviceInfo->Model;
	$arr['BRAND.Product.description'] = $system_conf->DeviceInfo->DeviceName;
	$arr['BRAND.Product.productid'] = $system_conf->DeviceInfo->hostname;
	$arr['VERSION.bootloader'] = "";
	$arr['VERSION.kernel'] = $system_conf->DeviceInfo->ModuleVersion;
	$arr['VERSION.firmware'] = $system_conf->DeviceInfo->FirmwareVersion;
	$arr['VERSION.description'] = "";
	$arr['VERSION.revision'] = $system_conf->DeviceInfo->BuildVersion;
	$arr['VERSION.hwrevision'] = "";
	$arr['VERSION.serialno'] = $system_conf->DeviceInfo->SerialNumber;
	$arr['VERSION.db'] = "";

}


if ($_GET['group'] == 'all' || $_GET['group'] == 'network') {
    $arr['NETWORK.Eth0.hostname']   = trim($system_conf->DeviceInfo->OnvifConf->hostname);
    $arr['NETWORK.Eth0.ipversion']  = 'ip4';
    $arr['NETWORK.Eth0.dhcp.enable']= trim($net_conf->IPv4->Type) == 0 ? 'no': 'yes';
    $arr['NETWORK.Eth0.mac']        = trim($net_conf->HwAddress);
    $arr['NETWORK.Eth0.subnet']     = trim($net_conf->IPv4->SubnetMask);
    $arr['NETWORK.Eth0.gateway']    = trim($net_conf->IPv4->Gateway);
    $arr['NETWORK.Eth0.mtu']        = $net_conf->MTUSetting->Value;
    $arr['NETWORK.Http.enable']     =  'yes';
    $arr['NETWORK.Http.port']       = $net_conf->Protocols->Protocol[0]->Port;
    $arr['NETWORK.Http.authentype'] = 'digest';
    $arr['NETWORK.Https.port']      = $net_conf->Protocols->Protocol[2]->Port;
    $arr['NETWORK.Rtsp.port']       = $net_conf->Protocols->Protocol[1]->Port;

// $data['control_port'] = 0;
// $data['video_port']   = 0;
// $data['at_port']      = 0;
// $data['ar_port']      = 0;
   
// $data['ipv6_enable']  = 0;

    $arr['NETWORK.Eth0.dhcp.ipaddress']  = trim($net_conf->IPv4->DynamicIpAddr);
    $arr['NETWORK.Eth0.ipaddress']  = ($net_conf->IPv4->Type == 0 ) ? trim($net_conf->IPv4->StaticIpAddr) : trim($net_conf->IPv4->DynamicIpAddr);

    if($net_conf->DNS->Type == 0)    {
        $arr['NETWORK.Dns.preferred']   = trim($net_conf->DNS->DNSManualAddr0);
        $arr['NETWORK.Dns.alternate0']  = trim($net_conf->DNS->DNSManualAddr1);	
    }
    else  {
        $arr['NETWORK.Dns.preferred']   = trim($net_conf->DNS->DNSDynamicAddr0);
        $arr['NETWORK.Dns.alternate0']  = trim($net_conf->DNS->DNSDynamicAddr1);
    }

    $arr['NETWORK.Eth0.Autoip.enable']  = $net_conf->ZeroConfig->Enabled;
    $arr['NETWORK.Eth0.Autoip.ipaddress']=trim($net_conf->ZeroConfig->Addr);
    $arr['NETWORK.Upnp.enable']         = trim($net_conf->UpnpSetting->Enabled) ? 'yes': 'no';
    $arr['NETWORK.Upnp.friendlyname']   = trim($net_conf->UpnpSetting->FriendlyName);
}

if ($_GET['group'] == 'all' || $_GET['group'] == 'vca') {
    // $body = file_get_contents("/mnt/plugin/.config/vca-cored/configuration/api.json");
    $body = file_get_contents("http://127.0.0.1/cgi-bin/admin/vca-api/api.json");
    $arr_v = dot_flatten(json_decode($body, true));
    
    $arr_v['VCA.Ch0.Lc0.licenseinfo'] = isset($arr_v['licenses.vca.0.name']) ? $arr_v['licenses.vca.0.name'] : '';
    $arr_v['VCA.Ch0.Lc1.licenseinfo'] = isset($arr_v['licenses.vca.1.name']) ? $arr_v['licenses.vca.1.name']  : '';
    $arr_v['VCA.Ch0.Hm.enable'] = 'no';
    $arr_v['FD.enable'] = 'no';
    $arr_v['FD.ch0.enable'] = 'no';

    for($i=0, $m=0, $n=0; $i<40; $i++) {
        if(isset($arr_v['observables.'.$i.'.typename']) && $arr_v['observables.'.$i.'.typename'] == 'vca.observable.Counter') {
            $arr_v['VCA.Ch0.Ct'.$m.'.enable'] = 'yes';
            $arr_v['VCA.Ch0.Ct'.$m.'.name']= $arr_v['observables.'.$i.'.name'];
            $arr_v['VCA.Ch0.Ct'.$m.'.color'] = '0,0,0';
            $arr_v['VCA.Ch0.Ct'.$m.'.points'] = $arr_v['observables.'.$i.'.x'].':'.$arr_v['observables.'.$i.'.y'];
            $arr_v['VCA.Ch0.Ct'.$m.'.nbrofsrc'] = '1';
            $arr_v['VCA.Ch0.Ct'.$m.'.count'] = $arr_v['observables.'.$i.'.count'];
            $arr_v['VCA.Ch0.Ct'.$m.'.uid'] = $i;
            $arr_v['VCA.Ch0.Ct'.$m.'.Sc0.enable'] = 'yes';
            $arr_v['VCA.Ch0.Ct'.$m.'.Sc0.type'] = 'inc';
            $arr_v['VCA.Ch0.Ct'.$m.'.Sc0.source'] = 0;
            $m++;

        }
        else if(isset($arr_v['zones.'.$i.'.name'])){
            $arr_v['VCA.Ch0.Zn'.$n.'.enable'] = $arr_v['zones.'.$i.'.detection'] ? 'yes': 'no'; 
            unset($arr_v['zones.'.$i.'.detection']);
            $arr_v['VCA.Ch0.Zn'.$n.'.name'] = $arr_v['zones.'.$i.'.name'];
            unset($arr_v['zones.'.$i.'.name']);
            $arr_v['VCA.Ch0.Zn'.$n.'.type'] = 'alarm';
            $arr_v['VCA.Ch0.Zn'.$n.'.style'] = $arr_v['zones.'.$i.'.polygon'] ? 'polygonline' : 'line';
            unset($arr_v['zones.'.$i.'.polygon'] );
            $arr_v['VCA.Ch0.Zn'.$n.'.color']= $arr_v['zones.'.$i.'.colour.r'].','.$arr_v['zones.'.$i.'.colour.g'].','.$arr_v['zones.'.$i.'.colour.b'];
            unset($arr_v['zones.'.$i.'.colour.r']);
            unset($arr_v['zones.'.$i.'.colour.g']);
            unset($arr_v['zones.'.$i.'.colour.b']);
            $arr_v['VCA.Ch0.Zn'.$n.'.points'] = $arr_v['zones.'.$i.'.points.0.x'].':'.$arr_v['zones.'.$i.'.points.0.y'];
            unset($arr_v['zones.'.$i.'.points.0.x']);
            unset($arr_v['zones.'.$i.'.points.0.y']);
            for($j=1; $j<40; $j++){
                if (isset($arr_v['zones.'.$i.'.points.'.$j.'.x'])) {
                    $arr_v['VCA.Ch0.Zn'.$n.'.points'] .= ','.$arr_v['zones.'.$i.'.points.'.$j.'.x'].':'.$arr_v['zones.'.$i.'.points.'.$j.'.y'];
                    unset($arr_v['zones.'.$i.'.points.'.$j.'.x']);
                    unset($arr_v['zones.'.$i.'.points.'.$j.'.y']);
                }
            }
            $arr_v['VCA.Ch0.Zn'.$n.'.uid']= $i;
            unset($arr_v['zones.'.$n.'.channel']);
            $n++;
        }
    }
    $arr = array_merge($arr, $arr_v);

    $arr_c= array();
    $fname = "/mnt/plugin/crpt/crpt.ini";
    if (file_exists($fname)) {
        $config = parse_ini_file($fname);    
        $arr_c['VCA.Ch0.Crpt.Db.enable'] = $config['crpt.enable'] ? 'yes':'no';
        $arr_c['VCA.Ch0.Crpt.Db.storage'] = 'iflash';
        $arr_c['VCA.Ch0.Crpt.Db.realstorage'] = 'iflash';
        $arr_c['VCA.Ch0.Crpt.Db.maxsize'] = 0;
        $arr_c['VCA.Ch0.Crpt.Db.nbroftable'] = 4;
        for($i=0; $i<4; $i++) {
            $arr_c['VCA.Ch0.Crpt.Db.Tb'.$i.'.enable'] = $config['table'.$i.'.enable'] ? 'yes':'no';
            $arr_c['VCA.Ch0.Crpt.Db.Tb'.$i.'.sampling'] = $config['table'.$i.'.interval'];
            $arr_c['VCA.Ch0.Crpt.Db.Tb'.$i.'.rollcount'] = $config['table'.$i.'.rollovercount'];
        }
    }
    $arr = array_merge($arr, $arr_c);    


}

$str = "";
foreach($arr as $key =>$val){
    $str .= $key."=".$val."\r\n";
}
Header('Content-type: text/json; charset=UTF-8');
print $str.PHP_EOL;
print "end of param";
?>
