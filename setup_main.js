var TimerId = 0;
var onPreview = false;
var previousPage;
var channel = 0 ;
var relayout_index = 0 ;
var camera_init_flag ;//= false;		
var VLCManager = new VLC(null, VideoInputInfo, capInfo);
var ajaxQueue = [];
var dnsIntervals = [];
var AlignmentWindow = null;
//[UDP technology] modify show menu by xml file -start
//udp_version=1.0.1
var isVCALicensed = false;
var prevdom = localStorage.getItem("target_dom");
var prevtab = localStorage.getItem("target_tab");
localStorage.removeItem("target_dom");
localStorage.removeItem("target_tab");
//[UDP technology] modify show menu by xml file -end
function refreshMenuContent(cmd)
{
	progressUI(false);
	if(cmd == "reload"){
		setTimeout(function(){ document.location.reload();}, 40000);
	}
	else if(cmd == "all_factory_set_reload"){
		setTimeout(function(){ opener.parent.location.reload();}, 40000);
	}
	else if(cmd == "wiper_set"){ // overview index page reload 임시 처리
		opener.parent.location.reload();
	}
	//[UDP technology] modify show menu by xml file -start
	else if(cmd && cmd != ""){
		localStorage.setItem("target_tab", "#" + cmd.split("/")[0]);
		localStorage.setItem("target_dom", "#" + cmd.split("/")[1]);
		document.location.reload();
	}//[UDP technology] modify show menu by xml file -end
	else {
		previousPage = null;
		$("[class=select_minor]").trigger("click");
	}
}
function onSuccessRequest(req)
{
	//alert("The system will be rebooted. Please close this setup page and reconnect after about 45 sec.");
	alert(getLanguage("msg_reboot_45sec_message"));
}
function popup_init(){
	$("#system").trigger("click");
	$("#User_Management").trigger("click");
	
	if( opener != undefined ) opener.popupflag = 0 ;		
}
function popup_ctrl(){
	
	if( opener == undefined ){
		$("ul").first().trigger("click");
		$("li").first().trigger("click");
		return 0 ;
	}
		
	if( opener.popupflag  == 1 &&  opener != undefined ) popup_init(); // click setup in popup window	
	else{
		$("ul").first().trigger("click");
		$("li").first().trigger("click");
	}
	//[UDP technology] modify show menu by xml file -start
	if(prevdom) {
		$target_dom = $(prevtab).find(prevdom);
		$target_dom.trigger("click");
		$target_dom.addClass("select_minor");	
	}//[UDP technology] modify show menu by xml file -end
	
}
function onLoadPage()
{
	dependecy_menu();
	getJson();
	initUI(); 
	initEvent();
	dependency_css();     //lang.js
	popup_ctrl();
}
/*************************** FOR NEW UI ************************************/
var video= {	name: "Video&Audio",
				menu: [[ "Video", "setup_basic_video.cgi"], 
				[ "osd", "setup_basic_osd.cgi"],
				]};

if( 1 ){
	VLCManager.preview_jpeg = true;
	var obj = new Array();
	obj[0] = ["roi","setup_basic_roi.cgi"];
	$.merge(video.menu, obj);
} else {
	VLCManager.preview_jpeg = false;
}
if( capInfo.audio_in || capInfo.audio_out ) {
	$.merge(video.menu, [["audio", "setup_basic_audio.cgi"]]);
}
if(smartcontrol == 1 && capInfo.camera_module != "s2l_internal_isp" && capInfo.image_sensor != "bt1120_1080p" && capInfo.image_sensor != "bt1120_720p" && capInfo.image_sensor != "bt1120_480p" && capInfo.camera_type != "PROXY_CLIENT" && capInfo.camera_type != "PROXY_SERVER" && capInfo.camera_type != "PREDATOR_CLIENT" && capInfo.camera_type != "PREDATOR_SERVER" && capInfo.camera_type != "PROXY_DUAL_CLIENT" && capInfo.camera_type != "PROXY_DUAL_SERVER"){
	if (capInfo["oem"] == 12){
		$.merge(video.menu, [["Rate_control", "setup_basic_smartrc.cgi"]]);
		$.merge(video.menu, [["Acf_plus", "setup_basic_smartacf.cgi"]]);
	} else if (capInfo["oem"] == 19 || capInfo["oem"] == 20 || capInfo["oem"] == 21){
		$.merge(video.menu, [["Rate_control_udp", "setup_basic_smartrc.cgi"]]);
		$.merge(video.menu, [["Acf_plus_stanley", "setup_basic_smartacf.cgi"]]);
	} else {
		$.merge(video.menu, [["Rate_control_udp", "setup_basic_smartrc.cgi"]]);
		$.merge(video.menu, [["Acf_plus_udp", "setup_basic_smartacf.cgi"]]);
	}
}

if(capInfo.camera_type == "fisheye_dewarping" || capInfo.camera_type == "360d")
{
	//$.merge(video.menu, [['Dewarping', "setup_basic_dewarp.cgi"]]);
}
else
{
	$.merge(video.menu, [['Privacy_Mask', "setup_camera_privacy.cgi"]]);
}

if (capInfo["oem"] == 19 || capInfo["oem"] == 20 || capInfo["oem"] == 21 || capInfo["oem"] == 10 || capInfo["oem"] == 11 || capInfo["oem"] == 13 || capInfo["oem"] == 25)
{
	//if((capInfo.camera_type == "normal" || capInfo.camera_type == "seekware") && capInfo.have_pantilt == 0)
	if( (capInfo.camera_type == "normal" || capInfo.camera_type == "4M" || capInfo.camera_type == "bridge") && capInfo.have_pantilt == 0)
		$.merge(video.menu, [["setup_corridor_setting", "setup_basic_corridor.cgi"]]);
}

var fisheye = { name:"fisheye", 
	menu: [[ "settings", "setup_fisheye_setting.cgi"],
	[ "calibration_center", "setup_fisheye_cali_center.cgi"],
	]};
/* ---------------------------------------------------------*/
var camera = { name : "camera", menu : [] };
var camInfo;
$.ajaxSetup({'async': false});
if( capInfo.camera_module == "sony_isp" || capInfo.camera_module == "wonwoo_isp" || capInfo.camera_module == "esca_isp" || capInfo.camera_module == "ytot_isp" || capInfo.camera_module == "ov_isp")
	var data = $.get("../sensor/ui/" + capInfo.camera_module + ".cgi");
else if( capInfo.camera_type == "thermal" )
	var data = $.get("../sensor/ui/" + "thermal" + ".cgi");
else if( capInfo.camera_type == "seekware")
	var data = $.get("../sensor/ui/" + "seek_thermal" + ".cgi");
else 
	var data = $.get("../sensor/ui/" + capInfo.image_sensor + ".cgi");

if( data.status == 200 )
{
	$.ajaxSetup({'async': true});
	camInfo = $.parseHTML(data.responseText);
	var index = camera.menu.length;
	camera.menu = new Array();
	for( var i = index ; i < camInfo.length ; i++) {
		if( camInfo[i].id == undefined) continue;
		if( camInfo[i].id == "Day_Night_Settings" && tdn == 0) continue;
		if( capInfo.camera_type == "ANPR") {
			var menu = camInfo[i].id ;
			if( menu == "Day_Night_Settings" || menu == "Backlight_Switch" || menu  == "White_Balance") {
				continue;
			}
		}

		camera.menu[index] = [ camInfo[i].id, camInfo[i], true ];
		index++;
	}
	camera.menu.unshift( ["setup_camera_profile", "setup_camera_profile.cgi",false ]);
	if( capInfo.camera_type == "PREDATOR_CLIENT" ) {
		camera.menu.unshift([ "ALIGNMENT", "setup_camera_alignment.cgi", false ]);
	}
	else if( (capInfo.camera_type == "PROXY_CLIENT" || capInfo.camera_type == "PROXY_DUAL_CLIENT") && capInfo.have_pantilt == 0 && capInfo.have_zoom > 1 && capInfo.have_focus > 0 ) {
		camera.menu.unshift([ "MFZ", "setup_camera_mfz.cgi", false ]);
	}
}
else 
{
	delete camera.menu[0];
}
/* ---------------------------------------------------------*/

if(capInfo.camera_type != "CUBE") {
	var network = {  name: "network",
			   menu:[['status', "setup_network_status.cgi"],
			   		 ["Network_Settings", "setup_network_tcp_ip.cgi"], 
			   		 ["AUTO_IP", "setup_network_zeroconfig.cgi"], 
			   		 ["ONVIF", "setup_network_onvif.cgi"], 
					 ["UPNP", "setup_network_upnp.cgi"], 
					 ['DDNS', "setup_network_ddns.cgi"],
					 ["FTP", "setup_transfer_ftp.cgi"],
					 ["SMTP", "setup_transfer_smtp.cgi"],
			   		 ["SNMP", "setup_network_snmp.cgi"],
			 		 ["INODE", "setup_transfer_inode.cgi"],
			   		 ["HTTP_ACTION", "setup_transfer_http_action.cgi"],
			   		 ["RTSP_STATUS", "setup_network_rtsp.cgi"]
					]};
}else
{
	var network = {  name: "network",
			   menu:[['status', "setup_network_status.cgi"],
			   		 ["Network_Settings", "setup_network_tcp_ip.cgi"], 
					 ["Wi-Fi_Settings", "setup_network_iot_wifi.cgi"],
			   		 ["AUTO_IP", "setup_network_zeroconfig.cgi"], 
			   		 ["ONVIF", "setup_network_onvif.cgi"], 
					 ["UPNP", "setup_network_upnp.cgi"], 
					 ['DDNS', "setup_network_ddns.cgi"],
					 ["FTP", "setup_transfer_ftp.cgi"],
					 ["SMTP", "setup_transfer_smtp.cgi"],
			   		 ["SNMP", "setup_network_snmp.cgi"],
			 		 ["INODE", "setup_transfer_inode.cgi"],
			   		 ["HTTP_ACTION", "setup_transfer_http_action.cgi"],
			   		 ["RTSP_STATUS", "setup_network_rtsp.cgi"]
					]};

}

if(local_rec)
{
	var record = { name: "record",
		menu:[['record_management', "setup_local_record_management.cgi"],
		["storage", "setup_event_storage.cgi"]
		]};
}else
{
	var record = { name: "record",
		menu:[['record_management', "setup_record_management.cgi"],
		["record_list", "setup_record_list.cgi"], 
		["storage", "setup_event_storage.cgi"]
		]};
}
var event = {	name: "events",
			 	menu: [//[ "alarm", "setup_event_alarm_input.cgi"],		
					["event_rules", "setup_event_event_rules.cgi"],
					["schedule", "setup_event_schedule.cgi"],
					["motion", "setup_basic_motion.cgi"],
					["temperature", "setup_event_temperature.cgi"],
					["digital_input", "setup_io_sensor_input.cgi"],
					["temperature_measurement", "setup_event_temperature_detect.cgi"], // for thermal
					["temperature_detect", "setup_event_seekware_temperature_detect.cgi"], // for seek thermal
				   ]};

if( capInfo.camera_type == "seekware") {
	for(var i = 0 ;  i < event.menu.length ; i++)
	{
		if(event.menu[i][0] == "temperature")
			event.menu[i][0] = "temperature_seek";
	}
}


var action = { 	name : "trigger_action",
				menu : [["action_rules", "setup_event_action_rules.cgi"],
						["transfer", "setup_transfer_transfer_setup.cgi"],
						["digital_output", "setup_io_relay_output.cgi"],
					]};
//[UDP technology] modify show menu by xml file -start
	var vca = {};
	var vcaMenu = "";
	var isvcaMenu = "";
	var addMainmenu = [];
	var addMenuLoc = [];
	var addSubmenu = [];
	var addSubcgi = [];
	var text = getXmlData();
	var parser = new DOMParser();
	var xmlDoc = parser.parseFromString(text,"text/xml");
	var length = xmlDoc.querySelectorAll('plugin_info').length;
	if( xmlDoc ) {
		length = xmlDoc.querySelectorAll('basefwmenu').length;
		var tmpMainmenu = "";
		var tmpMenuLoc = 0;
		var tmpSubmenu = "";
		var tmpSubcgi = "";
		var isShowMenu = "";
		for(var i = 0 ; i < length ; i++) {
			var newMenu = {};
			var curStatus = xmlDoc.getElementsByTagName("status")[i].childNodes[0]?xmlDoc.getElementsByTagName("status")[i].childNodes[0].nodeValue.toLowerCase():'none';
			isShowMenu = xmlDoc.getElementsByTagName("showingmenu")[i].childNodes[0]?xmlDoc.getElementsByTagName("showingmenu")[i].childNodes[0].nodeValue.toLowerCase():'none';
			tmpMainmenu = xmlDoc.getElementsByTagName("mainmenuname")[i].childNodes[0]?xmlDoc.getElementsByTagName("mainmenuname")[i].childNodes[0].nodeValue.toLowerCase():'none';
			tmpMenuLoc = xmlDoc.getElementsByTagName("showingloc")[i].childNodes[0]?xmlDoc.getElementsByTagName("showingloc")[i].childNodes[0].nodeValue.toLowerCase():'none';
			if((isShowMenu == "yes") && !(tmpMainmenu == "video" || tmpMainmenu == "fisheye" || tmpMainmenu == "camera" || tmpMainmenu ==  "network" || tmpMainmenu ==  "action" 
				|| tmpMainmenu ==  "event" || tmpMainmenu ==  "record" || tmpMainmenu ==  "security" || tmpMainmenu ==  "system"))
			{
				addMenuLoc.push(tmpMenuLoc);
				newMenu = { name : tmpMainmenu, menu : [] };
				newMenu.menu = new Array();
			}
			tmpSubmenu = xmlDoc.getElementsByTagName("basefwmenu")[i].getElementsByTagName("submenuname");
			tmpSubcgi = xmlDoc.getElementsByTagName("basefwmenu")[i].getElementsByTagName("cgi");
			addSubmenu = [];
			addSubcgi = [];
			//if(tmpMainmenu == "vca") getVCALicense(curStatus);
			for(var j = 0 ; j < tmpSubmenu.length ; j++) {
				var newSubmenu = tmpSubmenu[j].childNodes[0]?tmpSubmenu[j].childNodes[0].nodeValue.toLowerCase():'none';
				addSubmenu.push(newSubmenu);
				if (j < tmpSubcgi.length) { 
					var newSubcgi = tmpSubcgi[j].childNodes[0]?tmpSubcgi[j].childNodes[0].nodeValue.toLowerCase():'none';
					addSubcgi.push(newSubcgi);
				}
				/* if(tmpMainmenu == "vca" && curStatus == "running" && !isVCALicensed) {
					if(!(newSubmenu == "enable_vca" || newSubmenu == "license")) {
						continue;
					}
				} */
				if((isShowMenu == "yes") && (tmpMainmenu == "video" || tmpMainmenu == "fisheye" || tmpMainmenu == "camera" || tmpMainmenu ==  "network" || tmpMainmenu ==  "action" 
				|| tmpMainmenu ==  "event" || tmpMainmenu ==  "record" || tmpMainmenu ==  "security" || tmpMainmenu ==  "system"))
				{
					eval(tmpMainmenu).menu.push([ addSubmenu[j], addSubcgi[j]]);
				}
				else if(isShowMenu == "yes")
					newMenu.menu.push([ addSubmenu[j], addSubcgi[j]]);
				/* if(tmpMainmenu == "vca" && curStatus == "stopped") {
					break;
				} */
			}
			if(isShowMenu == "yes" && !(tmpMainmenu == "video" || tmpMainmenu == "fisheye" || tmpMainmenu == "camera" || tmpMainmenu ==  "network" || tmpMainmenu ==  "action" 
			|| tmpMainmenu ==  "event" || tmpMainmenu ==  "record" || tmpMainmenu ==  "security" || tmpMainmenu ==  "system"))
				addMainmenu.push(newMenu);
		}
	}
//[UDP technology] modify show menu by xml file -end
if( capInfo["oem"] == 12){
	var security = { 
		name: "security",
		menu : [
			["cyber_vigilant", "setup_security_ip_filter.cgi"],
			["rtsp_auth", "setup_security_rtsp_authentication.cgi"],
			["ieee_8021x", "setup_security_ieee_8021x.cgi"],
			["https", "setup_security_https.cgi"],
			["Certificates", "setup_security_certificates.cgi"],
			["Service", "setup_security_service.cgi"],
		]};
}else if( capInfo["oem"] == 2)
{
	var security = { 
		name: "security",
		menu : [
			["ip_address_filter", "setup_security_ip_filter.cgi"],
			["rtsp_auth", "setup_security_rtsp_authentication.cgi"],
			["ieee_8021x", "setup_security_ieee_8021x.cgi"],
			["https", "setup_security_https.cgi"],
			["Certificates", "setup_security_certificates.cgi"],
			// ["Service", "setup_security_service.cgi"],
            ["Auto_lock", "setup_security_autolock.cgi"],
		]};
}else{
	var security = { 
		name: "security",
		menu : [
			["ip_address_filter", "setup_security_ip_filter.cgi"],
			["rtsp_auth", "setup_security_rtsp_authentication.cgi"],
			["ieee_8021x", "setup_security_ieee_8021x.cgi"],
			["https", "setup_security_https.cgi"],
			["Certificates", "setup_security_certificates.cgi"],
			// ["Service", "setup_security_service.cgi"], // <-- do not display, by hanskim
		]};
}
var PTZ = {
	name: "PTZ",
	menu : [
		["setup_PTZ_settings", "setup_ptz_settings.cgi"],
	]};
if( capInfo.camera_module == "ov_isp" ){  // overview mode
	$.merge(PTZ.menu, [["setup_PTZ_advanced", "setup_ptz_advanced.cgi"]]);
}
if( capInfo.camera_module == "ov_isp" && capInfo["oem"] == 24 ){  // overview mode
	$.merge(PTZ.menu, [["setup_PTZ_shortcuts", "setup_ptz_shortcuts.cgi"]]);
}
if(userInfo.pwchange == 0){
    var system = { 
        name:"system",
        menu: [
            ["User_Management", "setup_system_users.cgi"],
        ]};

    var Tabs = [ system ];
    
}
else{
	var system = { 
		name:"system",
		menu: [
			["System_Information", "setup_system_capability.cgi"],
			["System_diagnostics", "setup_system_diagnostics.cgi"],
			["setup_system_configuration", "setup_system_configuration.cgi"],
			["rs485", "setup_system_rs485.cgi"],
			["firmware_update", "setup_system_firmware_update.cgi"],
			["Date&Time_Settings", "setup_system_date_time.cgi"],
			["Dst_Settings", "setup_system_dst.cgi"],
			["User_Management", "setup_system_users.cgi"],
			["System_log", "setup_system_log.cgi"],
			["Language", "setup_system_language.cgi"],
			["Factory_Reset", "setup_system_default_set.cgi"],
			["restart", "restart"] ,
			["Open_Source", "setup_system_open_source.cgi"],
			["Plug_in", "setup_system_plugin_upload.cgi"],
		]};
	
  	var Tabs = [ video, fisheye, camera, network, action, event, record, security, PTZ, system ];
	//[UDP technology] modify show menu by xml file -start
	if(addMainmenu && addMainmenu != "none") {
		for(var i = 0 ; i < addMainmenu.length ; i++) {
			Tabs.splice(addMenuLoc[i], 0, addMainmenu[i]);
		}
	}
	//[UDP technology] modify show menu by xml file-end
}
//[UDP technology] modify show menu by xml file-start
function readTextFile(file)
{
	var allText = '';
	var rawFile = new XMLHttpRequest();
	rawFile.open("GET", file, false);
	rawFile.onreadystatechange = function ()
	{
		if(rawFile.readyState === 4)
		{
			if(rawFile.status === 200 || rawFile.status == 0)
			{
				allText = rawFile.responseText;
			}
		}
	}
	rawFile.send(null);
	return allText;
}
function getXmlData()
{
	var timestamp = new Date().getTime();
	var file = "/plugin_info_list.xml?timestamp="+timestamp;
	var xmlDoc = readTextFile(file);//parser.parseFromString(text,"text/xml");
	return xmlDoc;
}
function getVCALicense(curStatus)
{
	if(curStatus == "running") {
		$.ajaxSetup({'async': false});
		$.ajax({
			type:'GET',
			url: "/cgi-bin/admin/vca-api/api/licenses/vca",
			contentType: 'application/json',
			data: {},
			success: function(msg){
				var licenseCnt = Object.keys(msg).length;
				isVCALicensed = (licenseCnt > 0)?true:false;
				//VLCManager.timoutVal = 200;
			},
			error: function(error) {
				console.log(error);
				refreshMenuContent();
			}
		});
		$.ajaxSetup({'async': true});
	}
}
//[UDP technology] modify show menu by xml file-end
function dependecy_menu(){	
	if( (systemOption & SYSTEM_OPTION_DW_EDGE ) == SYSTEM_OPTION_DW_EDGE ) {
		record['name'] = "EDGE";
		record.menu = [
			["setup_spectrum_edge", "setup_edge_dw.cgi"],
			["storage", "setup_event_storage.cgi"]];

		Util.remove_menu(2, "Dst_Settings");
	}
	
	if (configBackup == 0) { // DW, COX, DTI, CBCA, UR_SECURE, VCA, WAVESYS, JOGAN, ClickIT, LANACCESS 제외 하고
		Util.remove_menu( capInfo["oem"] , "setup_system_configuration" );
	}

	if ( supportPlugin == 0 ){
		Util.remove_menu( capInfo["oem"] , "Plug_in" );
	}

	if(capInfo.is_proxy_camera){
		Util.remove_menu( null , "setup_system_configuration" );
	}

	Util.remove_menu( 2 , "Language" ); //DW
	Util.remove_menu( 2 , "setup_camera_profile" );
	Util.remove_menu( 2 , "schedule" );	
	if(capInfo["oem"] != 2){
		Util.remove_menu( capInfo["oem"] , "HTTP_ACTION" );
    }
	Util.remove_menu( 3 , "System_log" );	

	Util.remove_menu( 6 , "AUTO_IP" );  //INODIC
	Util.remove_menu( 6 , "ONVIF" );
	Util.remove_menu( 6 , "SNMP" );
	Util.remove_menu( 6 , "RTSP_STATUS" );
	
	Util.remove_menu( 6 , "ieee_8021x" );
	Util.remove_menu( 6 , "https" );
	Util.remove_menu( 6 , "Certificates" );	
	Util.remove_menu( 6 , "Service" );	
	
	Util.remove_menu( 9 , "AUTO_IP" );  //RVI
	Util.remove_menu( 9 , "Service" );

	Util.remove_menu( 12 , "Language" );  //IV
	Util.remove_menu( 12 , "AUTO_IP" );
	Util.remove_menu( 12 , "UPNP" );
	Util.remove_menu( 12 , "Service" );

	if(capInfo["oem"] != 19){ // STANLEY ONLY
		Util.remove_menu( capInfo["oem"] , "INODE" );
    }

	if( capInfo['sensor_count'] < 1 )
	{		
		Util.remove_menu( null , "digital_input" );
	}
	if( capInfo['relay_count'] < 1 )
	{
		Util.remove_menu( null , "digital_output" );
	}
	if( capInfo['rs485'] < 1 )
	{
		Util.remove_menu( null , "rs485" );
	}
	if( capInfo.camera_type != "thermal" )
	{
		Util.remove_menu( null, "temperature_measurement");
	}
	if( capInfo.camera_type != "seekware" )
	{
		Util.remove_menu( null, "temperature_detect");
	}
	if( capInfo.camera_type == "thermal" )
	{
		Util.remove_menu( null, "setup_camera_profile" );
	}
	if( capInfo.camera_type == "seekware" )
	{
		Util.remove_menu( null, "Shutter_Settings" );
	}

	if( !capInfo.temperature_support ) {
		Util.remove_menu( null , "temperature" );
	}
	if( capInfo.camera_type != "CUBE")
	{
		Util.remove_menu( null , "Wi-Fi_Settings" );
	}
	
	for(var i = 0 ; i < Tabs.length ; i++) {
		if( Tabs[i] == record && capInfo.have_sdcard == 0) {
			delete Tabs[i];
		}
	
		if( Tabs[i] == fisheye && capInfo.camera_type != "fisheye_dewarp"){
			delete Tabs[i];
		}

		if( Tabs[i] == PTZ && capInfo.camera_module != "wonwoo_isp" && capInfo.camera_module != "ytot_isp" && capInfo.camera_module != "ov_isp"){
			delete Tabs[i];
		}
	}
}

function initUI()
{
	/*
    name : resizeWindow();
    operation : Align the body position
                 - vetical   : middle;
                 - alignment : center;
    function alignWindow()
    {
        var height = $("body").height();
        if( (window.outerHeight > height) && (window.screen.height > 620))
            $("body").css("margin-top", (window.outerHeight-height)/3);   
    }
    */
	
	try {
		var pattern = new RegExp("/|&");
		
		
		if( window.openr == null )
		{
			$("body").css("margin-left", "auto").css("margin-right", "auto");
		}
		for(var i = 0 ; i < Tabs.length ; i++)
		{
			if( typeof(Tabs[i]) == "undefined") continue;
			var item = Tabs[i].name.replace(pattern, "_");

			if( i == 0 && capInfo["oem"] == 1)
            {
            $("#sub_menu").append("<ul id='" + item  + "'><span id=exp_" + item  + "> > </span>" + "VIDEO & AUDIO" + "</ul>");
            }
            else
            $("#sub_menu").append("<ul id='" + item  + "'><span id=exp_" + item  + "> > </span>" + getLanguage(Tabs[i].name) + "</ul>");
            

			// init CLICK event for title menu;
			$("#" + item).click(item, function(input){
				var exp_status = [" > "," ∨ "];
				var opened = $("ul[class=select_major]");
				if( opened.attr('id') != input.data) {
					opened.removeClass();
					opened.find('li').slideToggle(200);
					$("#exp_" + opened.attr("id")).text(exp_status[0]);

					$("#exp_"+ input.data).text(exp_status[1]);
					$("#" + input.data).addClass("select_major");
					$("#" + input.data).find('li').slideToggle(200);
				}
			});

			for(var j = 0 ; j < Tabs[i].menu.length ; j++) {
				var rename = Tabs[i].menu[j][0];
				var id = rename.replace(pattern,"_");
				var name = rename.replace("_", " ");
				if(rename=='schedule'){
					 if( capInfo["oem"] == 11 || capInfo["oem"] == 25 ){
					 	$("#" + item).append("<li id='" + id + "'href='" + Tabs[i].menu[j][1] + "'>" + getLanguage('recurrences') + "</li>");	
					 }else{
						$("#" + item).append("<li id='" + id + "'href='" + Tabs[i].menu[j][1] + "'>" + getLanguage(rename) + "</li>");
					 }
				}else{
					$("#" + item).append("<li id='" + id + "'href='" + Tabs[i].menu[j][1] + "'>" + getLanguage(rename) + "</li>");
				}

				// init CLICK EVENT for sub menu
				$target_dom = $("#" + item).find("#" + id);
				if( id == "restart" ){
					$("#" + item).find("#" + id).click( function(){
						if (confirm(getLanguage("msg_reboot_restart"))){
							$.ajax({
								type:'get',
								url: '/cgi-bin/admin/system.cgi',
								data: { msubmenu:'reset', action:'reboot'},
								success: onSuccessRequest,
								error: null
							});
						}
					});
				} else if( item == "camera") {
					$target_dom.click(id, function(input){
						ajaxQueue.forEach(function(req) {
							req.abort();
						});
						ajaxQueue = [];
						if( typeof(timeOutId) != "undefined") clearTimeout(timeOutId);
						$("li[class=select_minor]").removeClass();
						var html;
						var obj;
						$.ajaxSetup({'async': false});
						if( input.data == "ALIGNMENT" ){
							AlignmentWindow = window.open('./setup_camera_alignment.cgi', 'win_alignment', 'resizable=no, scrollbars=no, width=' + 1330+ 'px, height=' + 300  +'px');// left='+ opener_left +', top='+ opener_top +'');
							AlignmentWindow.focus();		
							return ;
						}
						else if( input.data == "MFZ" ){
	 						if(capInfo.camera_type == "PROXY_DUAL_CLIENT") {
								AlignmentWindow = window.open('./setup_camera_mfz.cgi', 'win_alignment', 'resizable=no, scrollbars=no, width=' + 800+ 'px, height=' + 450  +'px');// left='+ opener_left +', top='+ opener_top +'');
							}else{
								AlignmentWindow = window.open('./setup_camera_mfz.cgi', 'win_alignment', 'resizable=no, scrollbars=no, width=' + 1330+ 'px, height=' + 380  +'px');// left='+ opener_left +', top='+ opener_top +'');
							}
							AlignmentWindow.focus();		
							return ;
						}
						// video laod 
						if( !onPreview ) {
							VLCManager.obj = null;
							$("#" + input.data).addClass("select_minor");	
							html = "setup_camera_preview.cgi";
							$("#tabs").load(html);

							if( VLCManager.obj == null) {
								var sensor = { 'width' :  VideoInfo[0].resolution.split('x')[0],
									'height': VideoInfo[0].resolution.split('x')[1] };
								var preview_out= { 'width' : 0, 'height' : 288};
								if( sensor.width * 9 == sensor.height * 16 ) { 
									preview_out.width  = preview_out.height * 16 / 9;
                                } 
								else if( sensor.width * 3 == sensor.height * 4 ){
                                    preview_out.width  = preview_out.height * 4 / 3;
                                }
                                else if(sensor.width == sensor.height){ 
                                    preview_out.width  = preview_out.height;
                                }
								else {
									preview_out.width = preview_out.height * (sensor.width / sensor.height); 
								}

								if(corridor_mode)
								{
									preview_out.width = preview_out.width/4*3;
									preview_out.height = preview_out.height/4*3;
									$("#vlc_box").width(preview_out.height).height(preview_out.width);
									$("#display_box").css("padding-left", ($("#display_box").width() - preview_out.height) /2);
								}
								else
								{
									$("#vlc_box").width(preview_out.width).height(preview_out.height);
									$("#display_box").css("padding-left", ($("#display_box").width() - preview_out.width) /2);
								}
								VLCManager.setPlayInfo(userInfo, rtspPort);
								VLCManager.initPreview("vlc_box", true);
							}
							onPreview = true;
						}
						$.ajaxSetup({'async': true});
						html = $("#" + input.data).attr("href");
						// data load
						$("#" + input.data).addClass("select_minor");	
						for(var i=0; i < camera.menu.length ; i++) {
							obj = camera.menu[i];
							if( obj[0].replace(pattern, "_") != input.data ) continue;
							// js/init value reload
							if( previousPage != "CAMERA_SETUP" ){
								$.ajaxSetup({'async': false});
								$("#initValue").load("setup_camera_init.cgi");
								$.ajaxSetup({'async': true});
							}
							$("#motionOverlay").remove();
							if( obj[2] ) { //camera settings. it depend on sensor
								var sub_title =  obj[0];
								if(sub_title == "Image_Enhancement")
									$("#camTitle").text(getLanguage("Image_Enhancement"));
								else
									$("#camTitle").text(getLanguage(sub_title));
								$("#camContents").empty().append(obj[1]);
								$("#camSettings").show();
								$("#camOthers").hide();
								
								$.extend(true, CameraFunc, initialValue);
								
								init();      // sensor/js
								initLanguage();
								camera_init_flag = false;		 
								
								previousPage = "CAMERA_SETUP";
							} else { // others(privacy, profile)
								var data = $.get(html).done(function(){
									var pageInfo = $.parseHTML(data.responseText);
									$("#camTitle").empty().append(pageInfo[1].childNodes[0]).
									append(pageInfo[1].childNodes[1]);
									$("#camContents").empty().append(pageInfo[3].childNodes);
									$("#camOthers").empty().show().append(pageInfo[5].childNodes);
									$("#camSettings").hide();
									initLanguage();
									$.getScript(html.replace("cgi", "js"), function(){
										init();	
									});
								});
								previousPage = html;
							}
						}
					});
				} else {
					$target_dom.click(id, function(input){
						ajaxQueue.forEach(function(req) {
							req.abort();
						});
						ajaxQueue = [];
						var opened = $("li[class=select_minor]");
						if( opened.attr('id') != input.data) {
							channel = 0 ;
							relayout_index = 0 ;
						}
						if( typeof(timeOutId) != "undefined") clearTimeout(timeOutId);
						$("li[class=select_minor]").removeClass();
						var html;
						var obj;
						onPreview = false;
						html = $("#" + input.data).attr("href");
						$("#tabs").load(html, function(){initLanguage();clearTimeout(timeout);});
						var id = $("ul[class=select_major]").attr("id");
						$("#" + id ).find("#" + input.data).addClass("select_minor");
						previousPage = html;
					});
				}

			}
		}
	} catch (e) {
		console.log("FAIL : initUI()");
		console.log("LOG  : " + e );
	}
	Util.setOEM("setOEM");
	//    alignWindow();	
	if( capInfo["oem"] == 12){
		$('#cyber_vigilant').css('text-transform','none');
	}
	if(gLanguage == 5 || gLanguage == 4)  
	{   
		$("#Factory_Reset").css( "cssText", "font-size: 9px !important");
	} 
}
function initEvent()
{
    if(opener != null)
    {
        window.addEventListener('touchstart',parent_event,false); 
        window.addEventListener('click',parent_event,false); 
        window.addEventListener('keypress',parent_event, false); 
        function parent_event(){
            opener.parent.sessionTimeoutInit();
        }
    }
}
$(document).ready( function(){
//   getSystemClock();
	onLoadPage();
});
window.onunload = function(){
	if( AlignmentWindow ){
		AlignmentWindow.close(); 
	}
};
