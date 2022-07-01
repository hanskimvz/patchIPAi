//  excel to json >> http://beautifytools.com/excel-to-json-converter.php 
//  json to excel >> https://json-csv.com/   
var g_json = null;
var lang ='';
var g_json_tkey = new Object();

function getJson(){
	if(gLanguage == 0) 	   lang = "English";
	else if(gLanguage == 1) lang = "Korean";
	else if(gLanguage == 2) lang = "Japanese";
	else if(gLanguage == 3) lang = "Russian";
	else if(gLanguage == 4) lang = "French";
	else if(gLanguage == 5) lang = "Dutch";
	else if(gLanguage == 6) lang = "German";
	else if(gLanguage == 7) lang = "Spanish";
	else if(gLanguage == 8) lang = "Italiano";
	else if(gLanguage == 9) lang = "Chinese";
	
	$.ajaxSetup({'async': false});
	$.getJSON('/js/lang.json', function(json) {
		//[UDP technology] Language adjustment when uploading plugin files - start
		if(fileExists('/js/pluginlang.json?t=' + Math.random())) {
			$.getJSON('/js/pluginlang.json', function(pluginjson) {
				for(i=0; i < pluginjson.language.length ; i++) {
					json.language.push(pluginjson.language[i]);
				}
			});
		}
		//[UDP technology] end
		g_json = json;
	});
	
	for(i=0; i < g_json.language.length ; i++)
	{
		g_json_tkey[g_json["language"][i]["key"]] = i ;	 // 	g_json_tkey["setup_enable"]=0	
	}
	
	$.ajaxSetup({'async': true});
}
//[UDP technology] Check file exists - start
function fileExists(url)
{
	var http = new XMLHttpRequest();
	http.open('HEAD', url, false);
	http.send();
	return http.status!=404;
}
//[UDP technology] end
function getLanguage(val){			
	   try{
			return g_json["language"][g_json_tkey[val]][lang];	
		}
		catch(err){		
			return val ;
			console.log( "getLanguage: "+val );	
		}	
}
function dependency_css(){
	  if(gLanguage == 2){                                           // japanese
		  $('head').append('<link  class="css_file" rel="stylesheet" href="/css/japanese.css" type="text/css" />');
	  }
	  else if( gLanguage == 3){
		  $('head').append('<link  class="css_file" rel="stylesheet" href="/css/russian.css" type="text/css" />');
	  }else if(gLanguage == 4 || gLanguage == 5 || gLanguage == 6 || gLanguage == 7 || gLanguage == 8){
		  $('head').append('<link  class="css_file" rel="stylesheet" href="/css/europe.css" type="text/css" />');
	  }else if(gLanguage == 9){
		$('head').append('<link  class="css_file" rel="stylesheet" href="/css/chinese.css" type="text/css" />');

	  }else{
		  if( $(".css_file").length > 0 )  $(".css_file").remove() ;			 		    	
	  }
}
function initLanguage()
{
	if(gLanguage == 0) 	   lang = "English";
	else if(gLanguage == 1) lang = "Korean";
	else if(gLanguage == 2) lang = "Japanese";
	else if(gLanguage == 3) lang = "Russian";
	else if(gLanguage == 4) lang = "French";
	else if(gLanguage == 5) lang = "Dutch";
	else if(gLanguage == 6) lang = "German";
	else if(gLanguage == 7) lang = "Spanish";
	else if(gLanguage == 8) lang = "Italiano";
	else if(gLanguage == 9) lang = "Chinese";

	$.ajaxSetup({'async': false});
	var strTr;
	
	$("[tkey]").each (function(){
		try{
			var strTr = g_json["language"][g_json_tkey[$(this).attr('tkey')]][lang];
		}
		catch(err){
			console.log( "not find " + $(this).attr ('tkey'));
			$(this).html($(this).attr ('tkey')); 	
		}
		$(this).html(strTr); 		
	});
	$.ajaxSetup({'async': true});
}
