
var menu = "LANGUAGE";
var settingList = ["language"];
var target = "languageInfo"
function initUI()
{
	var option = '';
	console.log(capInfo);
	if( capInfo['oem'] == 9 ){
		option += "<option value='0' >English</option>";
		option += "<option value='3' >Русский</option>";
	}else if( capInfo['oem'] == 8 ){
		option += "<option value='0' >English</option>";
		option += "<option value='2' >日本語</option>";
	// }else if( capInfo['oem'] == 10 || capInfo['oem'] == 11){
	// 	option += "<option value='0' >English</option>";
	// 	option += "<option value='4' >French</option>";
	// 	option += "<option value='6' >German</option>";
	// 	option += "<option value='7' >Spanish</option>";
	// 	option += "<option value='8' >Italiano</option>";
	}else if( capInfo['oem'] == 10 || capInfo['oem'] == 11){
		option += "<option value='0' >English</option>";
		option += "<option value='1' >한국어</option>";
		option += "<option value='9' >中文</option>";
	}
	else if( capInfo['oem'] == 19 || capInfo['oem'] == 20 || capInfo['oem'] == 21){
		option += "<option value='0' >English</option>";
		option += "<option value='3' >Russian</option>";
		option += "<option value='4' >French</option>";
		option += "<option value='5' >Dutch</option>";
		option += "<option value='6' >German</option>";
	}else if( capInfo['oem'] == 25 ){
		option += "<option value='0' >English</option>";
		option += "<option value='1' >한국어</option>";
		option += "<option value='2' >日本語</option>";
		option += "<option value='7' >Spanish</option>";
	}else{
		option += "<option value='0' >English</option>";
		option += "<option value='1' >한국어</option>";
		option += "<option value='2' >日本語</option>";
	}
	$("#language").append(option);
}
function initvalue()
{
	for( var i = 0 ; i < settingList.length ; i++)	
	{	
		var obj = $("#" + settingList[i]);
		var tag = obj.prop("tagName");
		if( tag == "SELECT" || tag == "INPUT")
		{
			obj.val( target[settingList[i]]);
		}	
	}	
	checkDependency()
}
function checkDependency()
{
	var index = languageInfo["language"] ;
	console.log( languageInfo["language"]);
	$("#language option[value="+index+"]" ).prop("selected" , true);
}			

function initEvent()
{
		$("#btOK").click(function(event) { 
		function onSuccessApply(msg)
		{
			var tmp= msg.trim().split('\n');
			console.log(tmp);
			if(tmp[0] == "OK")
			{		
				alert(getLanguage("msg_language_changed"));
			}
			else 
			{
				settingFail(menu, tmp[0]);
			}
			document.location.reload();
			//window.opener.document.location.reload();
//			$.ajaxSetup({'async': true});
//			$(opener.location).attr("href","javascript:location.reload();");   
//			$.ajaxSetup({'async': false});
		}
		function onFailApply()
		{
			settingFail(menu, "apply fail. retry again.");
			refreshMenuContent();
		}	

		var data = null;
		{
			var newValue;
			var orgValue;

			for( var i = 0 ; i < settingList.length ; i++)	
			{	
				var obj = $("#" + settingList[i]);

					if(($("[name = "+settingList[i]+"]").prop("type")) == "radio")  // radio 
					{
						newValue = $("[name="+settingList[i]+"]:checked").val();
					}
					else if(($("#" + settingList[i]).prop("type")) == "checkbox")  // checkbox
					{
						if(($("#" + settingList[i]).prop("checked")) == true)
							newValue = 1;
						else				
							newValue = 0;					
					}
					else // select , input 
					{
						newValue = obj.val();				
					}
					orgValue = target[settingList[i]];
					if( orgValue != newValue )
					{
						if( data == null)
							data = settingList[i] + "=" + newValue;
						else
							data += "&" + settingList[i] + "=" + newValue;
					}
				}
			}
				 
			if(data != null)
			{
				data = "msubmenu=language&action=apply&"+ data;
			} else {
				settingFail(menu, "NOTHING Change");
				return ;
			}
			$.ajax({
				type:"get",
				url: "/cgi-bin/admin/system.cgi",
				data: data,
				success: onSuccessApply, 
				error: onFailApply
			});
		});
}
function onLoadPage()
{   
	initUI();
	initEvent();
	initvalue();
}

$(document).ready( function() {
	onLoadPage();
});
