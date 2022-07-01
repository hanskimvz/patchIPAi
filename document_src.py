body_crpt_sh = """
#!/bin/sh
echo "################################################"
echo "### Enable Crond and Counting report service ###"
echo "################################################"

CRONDIR="/var/spool/cron"
FILECRON="/var/spool/cron/crontabs/root"
STRCRON="* * * * * /usr/bin/php-cgi /mnt/plugin/crpt/mk_ct_report.cgi" 

if [ ! -d $CRONDIR ]; then 
    echo "Create directory, $CRONDIR"
    mkdir $CRONDIR
fi

if [ ! -d $CRONDIR/crontabs ]; then 
    echo "Create directory, $CRONDIR/crontabs"
    mkdir $CRONDIR/crontabs
fi

if [ ! -f $FILECRON ]; then 
    echo "Create file, $FILECRON"
    echo "$STRCRON" > $FILECRON
fi

MODCRON=`cat $FILECRON | grep mk_ct_report.cgi | awk '{print $0}'`
# echo "$MODCRON"
if [ ! "$MODCRON" ] ;  then
    echo "appending string" 
    echo "\r\n$STRCRON" >> $FILECRON
fi

ES=`ps -ef |grep crond | grep -v grep | awk '{print $1}'`
# echo "$ES"
if [ ! "$ES" ] ;  then
    echo "Service Crond start" 
    /usr/sbin/crond
fi
"""

body_crpt_cgi = """
<?
$max_roll_over_count = 1440*90; // 90days

require('/root/web/cgi-bin/_define.inc');
require('/root/web/cgi-bin/class/system.class');
$shm_id = shmop_open(KEY_SM_SHARED_CONFIG, "a", 0, 0);
$system_conf = new CSystemConfiguration($shm_id);
shmop_close($shm_id);
$TimezoneIndex = $system_conf->SystemDatetime->TimeZoneIndex;
$timezone = "Etc/GMT".($TimezoneIndex-12 >0 ? "-".strval($TimezoneIndex-12): "+".strval(12-$TimezoneIndex));
date_default_timezone_set($timezone);

Header('Content-type: text/json; charset=UTF-8');
// cgi-bin/admin/vca-api/api.json
$filename = "/mnt/plugin/.config/vca-cored/configuration/api.json";
$filedb = "/mnt/plugin/.config/vca-cored/configuration/countreport.db";

if (!file_exists($filedb)) {
    file_put_contents($filedb,"");
}
$db_body = file_get_contents($filedb);
$arr_rs = json_decode($db_body, true);
if(!$arr_rs) {
	$arr_rs = array();
}

$json_body = file_get_contents($filename);
$arr = json_decode($json_body, true)['observables'];

// print_r($arr);
$timestamp = time();
$datetime = date("Y-m-d H:i:00", $timestamp);
$timestamp = strtotime($datetime);

array_push($arr_rs, ["timestamp"=>$timestamp, "datetime"=>$datetime, "counters"=>[]]);
$n = sizeof($arr_rs) -1;
if ($n>$max_roll_over_count){
    $arr_rs = array_shift($arr_rs);
}
for ($i=0; $i<sizeof($arr); $i++) {
	if ($arr[$i]['typename'] == 'vca.observable.Counter') {
		// array_push($arr_rs, ["timestamp"=>$timestamp, "datetime"=>$datetime, "idx"=>$i, "name"=>$arr[$i]['name'], "value"=>$arr[$i]['count']]);
		array_push($arr_rs[$n]['counters'], ["idx"=>$i, "name"=>$arr[$i]['name'], "value"=>$arr[$i]['count']]);
		// $arr_rs[$n][$arr[$i]['name']] = $arr[$i]['count'];
	}
}

// print_r($arr_rs);
$json_body = json_encode($arr_rs);
file_put_contents($filedb, $json_body);

// excute
// /usr/bin/php-cgi /mnt/plugin/mk_ct_report.cgi

// crontab -e
// * * * * * /usr/bin/php-cgi /mnt/plugin/mk_ct_report.cgi
?>
"""


body_view_crpt_cgi = """
<?
require('/root/web/cgi-bin/_define.inc');
require('/root/web/cgi-bin/class/system.class');
$shm_id = shmop_open(KEY_SM_SHARED_CONFIG, "a", 0, 0);
$system_conf = new CSystemConfiguration($shm_id);
shmop_close($shm_id);
$TimezoneIndex = $system_conf->SystemDatetime->TimeZoneIndex;
$timezone = "Etc/GMT".($TimezoneIndex-12 >0 ? "-".strval($TimezoneIndex-12): "+".strval(12-$TimezoneIndex));
date_default_timezone_set($timezone);

//validate Get param
foreach($_GET as $key=>$val){
    $_GET[$key] = strtolower($val);
}
// print_r($_GET);
if ( !isset($_GET['reportfmt']) || !in_array($_GET['reportfmt'], ['csv', 'table', 'json','chart'])){
    print ("<br>Error: reportfmt in  ['csv', 'table', 'json','chart']");
    exit();
}
if (!isset($_GET['order']) || !in_array($_GET['order'], ['asc', 'ascending', 'desc','descending'])){
    print ("<br>Error: order in ['asc', 'ascending', 'desc','descending']");
    exit();
}
if( !isset($_GET['sampling']) ||  (strval(intval($_GET['sampling'])) !=  strval($_GET['sampling'])) ||($_GET['sampling']%60 !=0) ) {
    print ("<br>Error: sampling must be integer and multipled by 60, 1 minute intervaly");
    exit();
}
if (!isset($_GET['value']) || !in_array($_GET['value'], ['abs', 'diff'])){
    print ("<br>Error: value in ['abs', 'diff']");
    exit();
}

function datestrtotime($str){
    global $start;
    global $last;
    global $step;
    $arr = ['yesterday','today','now', "thisweek", "thismonth", "lastweek", "lastmonth"];
    $str = strtolower($str);
    foreach($arr as $arr) {
        if (!strncmp($arr, $str, strlen($arr))) {
            $offset = str_replace($arr, "",$str);
            if ($arr == "thisweek") {
                $arr = date("Y-m-d 00:00:00", strtotime("last sunday"));
            }
            else if ($arr == "lastweek") {
                $arr = date("Y-m-d 00:00:00", strtotime("last sunday")-3600*24*7);
            }            
            else if ($arr == "thismonth") {
                $arr = date("Y-m-d 00:00:00", strtotime("first day of this Month"));
            }
            else if ($arr == "lastmonth") {
                $arr = date("Y-m-d 00:00:00", strtotime("first day of last Month"));
            }
            $ts = strtotime(date("Y-m-d H:i:00", strtotime($arr)));

            $ts += intval($offset);
            $str = date("Y-m-d H:i:s", $ts);
            break;
            // return $ts;
        }
    }
    $ts = strtotime($str);
    if($start > $ts){
        $ts = $start;
    }
    if($last < $ts){
        $ts = $last;
    }
    $ts = strtotime(date("Y-m-d H:i:00", ceil($ts/$step)*$step));
    return $ts;
}


// http://192.168.132.6/cgi-bin/operator/countreport.cgi?reportfmt=csv&to=now-600&counter=active&sampling=600&order=Ascending&value=diff&from=today
$filedb = "/mnt/plugin/.config/vca-cored/configuration/countreport.db";

if (!file_exists($filedb)) {
    file_put_contents($filedb,"");
}
$db_body = file_get_contents($filedb);
$arr = json_decode($db_body, true);
if (!$arr){
    $arr = array();
}
// print "<pre>"; print_r($arr); print "</pre>";
$start = $arr[0]['timestamp'];
$last  = $arr[sizeof($arr)-1]['timestamp'];
// print $start."-".$last;
$counters = array();
$ct_names = array();
foreach($arr as $arr_rs){
    foreach($arr_rs['counters'] as $ct){
        if (!in_array($ct['name'],$ct_names)) {
            array_push($ct_names, $ct['name']);
        }
        $counters[$arr_rs['timestamp']][$ct['name']] = $ct['value'];
    }
}

for ($s=$start; $s<=$last; $s+=60){
    foreach($ct_names as $ct_name){
        if (!isset($counters[$s][$ct_name])){
            $counters[$s][$ct_name] = $counters[$s-60][$ct_name];
        }
    }
}



// print (date("Y-m-d H:i:s", strtotime("today")));


$arr_rs = array();
$step = $_GET['sampling'];
$ts_from = datestrtotime($_GET['from']);
$ts_to = datestrtotime($_GET['to']);

$duration = ceil(($ts_to - $ts_from) / $step);

// print "\n\rfrom: ".$ts_from.", ".date("Y-m-d H:i:s",$ts_from);
// print "\n\rto: ".$ts_to.", ".date("Y-m-d H:i:s",$ts_to);
// print "\n\rstep: ".$step;
// print "\n\rduration: ".$duration;

$arr_ts = array();
$arr_rs = array();
for ($i=-1; $i<$duration; $i++){
    $arr_ts[$i] = $ts_from + $step *$i;
    if ($i <0){
        continue;
    }
    foreach($ct_names as $ct_name){
        if (!isset($counters[$arr_ts[$i-1]][$ct_name])){
            $counters[$arr_ts[$i-1]][$ct_name] = $counters[$arr_ts[$i]][$ct_name];
        }
        if($_GET['value'] == 'abs') {
            $arr_rs[$arr_ts[$i]][$ct_name] = $counters[$arr_ts[$i]][$ct_name];
        }
        else {
            $arr_rs[$arr_ts[$i]][$ct_name] = $counters[$arr_ts[$i]][$ct_name] - $counters[$arr_ts[$i-1]][$ct_name];
        }
    }
}

if ($_GET['reportfmt'] == 'json'){
    Header('Content-type: text/json; charset=UTF-8');
    $arr_t = array();
    foreach($arr_rs as $ts => $arr){
        $arr_t[date("Y-m-d H:i:00",$ts)] = $arr;
    }
    print json_encode($arr_t, JSON_PRETTY_PRINT);
    exit();
}

if ($_GET['order'] == 'desc' || $_GET['order'] == 'descending'){
    $arr_ts = array_reverse($arr_ts);
}


$tag_s = ""; $tag_p = ""; $tag_n = ","; $tag_l = "\r\n";
if ($_GET['reportfmt'] == 'table'){
    $tag_s = "<tr>"; $tag_p = "<td>"; $tag_n = "</td>"; $tag_l = "</tr>\r\n";
}

$table_body = $tag_s.$tag_p."Records:".$duration." Counter:".sizeof($ct_names).$tag_n;
$i=0;
foreach($ct_names as $ct_name){
    $table_body .= $tag_p.($i++).":".$ct_name.$tag_n;
}
$table_body .= $tag_l;

// print_r($ct_names);
// print_r($counters);

for ($i=0; $i<$duration; $i++){
    $ts = $arr_ts[$i];
    $table_body .= $tag_s.$tag_p.date("Y/m/d H:i:s", $ts).$tag_n;
    foreach($ct_names as $ct_name){
        $table_body .= $tag_p.$arr_rs[$ts][$ct_name].$tag_n;
    }
    $table_body .= $tag_l;
}

if ($_GET['reportfmt'] == 'table'){
    Header('Content-type: text/html; charset=UTF-8');
    $table_body = '<style type="text/css">
        body {background-color: #fff; color: #222; font-family: sans-serif;}
        pre {margin: 0; font-family: monospace;}
        a:link {color: #009; text-decoration: none; background-color: #fff;}
        a:hover {text-decoration: underline;}
        table {border-collapse: collapse; border: 0; box-shadow: 1px 2px 3px #eee;}
        .center {text-align: center;}
        .center table {margin: 1em auto; text-align: left;}
        .center th {text-align: center !important;}
        td, th {border: 1px solid #aaa; font-size: 75%; vertical-align: baseline; padding: 4px 5px;}
        input {border: 1px solid #aaa; font-size: 100%; vertical-align: baseline; padding: 4px 5px;}
    </style>
    <table>'.$table_body.'</table>';
    print $table_body;
    exit();
}
else if ($_GET['reportfmt'] == 'csv'){
    Header('Content-type: text/csv; charset=UTF-8');
    print $table_body;
    exit();
}
else if ($_GET['reportfmt'] == 'chart'){
    $arr_wcolor = array (
		'red' => 'rgb(255, 99, 132)', 
		'orange' => 'rgb(255, 159, 64)', 
		'yellow' => 'rgb(255, 205, 86)', 
		'green' => 'rgb(75, 192, 192)', 
		'blue' => 'rgb(54, 162, 235)', 
		'purple'=> 'rgb(153, 102, 255)', 
		'grey'=> 'rgb(201, 203, 207)', 
		'black'=> 'rgb(60, 60, 60)',
	);	
    $arr_t = array();
    $arr_ts = array();
    foreach($ct_names as $ct_name){
        $arr_d[$ct_name] = array();
    }
    foreach($arr_rs as $ts => $arr){
        array_push($arr_ts,date("Y-m-d H:i:00",$ts));
        foreach($arr as $ct_name => $val){
            // print $val;
            array_push($arr_d[$ct_name], $val);
        }
        // print_r($arr);
        
    }
    foreach($ct_names as $ct_name){
        $rand_color = array_shift($arr_wcolor);
        array_push($arr_t, ['label'=> $ct_name, 'data' => $arr_d[$ct_name], 'borderWidth'=>3, 'borderColor'=>$rand_color, 'backgroundColor'=>$rand_color, 'fill'=>false, 'tension'=>0.5]);
    }
    $x_labels = json_encode($arr_ts, true);
    $dataset = json_encode($arr_t, true);
    $str_js = '
        <script src="/js/Chart.bundle.min.js"></script>		
        <canvas id="myChart" width="1200" height="600"></canvas>
        <script>
            const ctx = document.getElementById("myChart").getContext("2d");
            let config =  {
                type: "line",
                data: {},
                options: {
                    responsive: false,
                    plugins: {
                        title: {
                            display: true,
                        },
                        legend:{
                            display:true,
                            position:"top",
                            labels:{
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode:"index",
                        axis:"y"
                    },
                    scales: {
                        x: {
                            display: true,
                            type: "time",
                            time: {
                                parser: "MM/DD/YYYY HH:mm",
                                tooltipFormat: "ll HH:mm",
                                unit: "day",
                                unitStepSize: 1,
                                displayFormats: {
                                "day": "MM/DD/YYYY"
                                }
                            },
                            title: {
                                display: true
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: "Count"
                            },
                            suggestedMin: 0,
                            suggestedMax: 200
                        }
                    }
                },
            };
            const myChart = new Chart(ctx, config);
            let data = {
                labels: '.$x_labels.',
                datasets: '.$dataset.'
            };
            myChart.data = data;
            myChart.update();
        </script>';
    print $str_js;
}

// print "<pre>"; print_r($arr_rs); print "</pre>";

?>
"""

body_lang_json_edit = """
<?
$help = '<style type="text/css">body {background-color: #fff; color: #222; font-family: sans-serif;}</style>
    </br>http://{camera_ip}/lang_json_edit.cgi?cat=[camera/vca]&mode=[insert/list/delete]&lang=[lang]
    ';
if (!isset($_GET['lang'])){
    print $help;
    exit();
}
else {
    $_GET['lang'] = trim(strtolower($_GET['lang']));
    $_GET['lang'][0] = strtoupper($_GET['lang'][0]);
}
if (!isset($_GET['cat'])) {
    $_GET['cat'] = 'camera';
}
if (!isset($_GET['mode'])){
    $_GET['mode'] = "list";
}
else if(! in_array($_GET['mode'], ['insert', 'list', 'delete', 'modify']) ) {
    print $help;
    exit();
}

if ($_GET['cat'] == 'camera') {
    $filename = "/root/web/js/lang.json";
}
else if ($_GET['cat'] == 'vca') {
    $filename = "/tmp/plugin/pluginlang.json";
}
else {
    exit();
}

$json_body = file_get_contents($filename);
$arr = json_decode($json_body, true)['language'];

if ($_GET['mode'] == 'insert'){
    // check if language is exist or not
    if (isset($arr[0][$_GET['lang']])){
        print "Language: ".$_GET['lang']." already exisit";
        exit();
    }

    for($i=0; $i<sizeof($arr); $i++ ) {
        if (!isset($arr[$i][$_GET['lang']])){
            $arr[$i][$_GET['lang']] = $arr[$i]['English'];
        }
    }
    $arr_t['language'] = $arr;
    print_r($arr_t);
    // $json = json_encode($arr_t);
    // file_put_contents($filename, $json);
    exit();
}
else if ($_GET['mode'] == 'modify'){
    // print_r($_GET);
    file_put_contents($filename.'.bak', $json_body);
    $_GET['value'] =  str_replace('__BUTTON', '<button class="button" id="change_pass">', $_GET['value']);
    $_GET['value'] =  str_replace('BUTTON__', '</button>', $_GET['value']);

    $arr[$_GET['id']][$_GET['lang']] = $_GET['value'];
    $arr_t['language'] = $arr;
    $json = json_encode($arr_t);
    file_put_contents($filename, $json);
    if ($_GET['cat'] == 'vca') {
        $json = json_encode($arr);
        $json= substr($json, 1, strlen($json)-2);
        file_put_contents("/mnt/plugin/vca/web/pluginlang.json",$json);
    }
    // print $json;
    print "key: ".$_GET['name'].", ".$_GET['lang'].": ".$_GET['value']." is modified: OK";
}
else {
    echo '
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <meta name="description" content="Responsive Bootstrap 4 Admin &amp; Dashboard Template">
            <meta name="author" content="Bootlab">
            <title id="title">Admin Tools</title>
            <style type="text/css">
                body {background-color: #fff; color: #222; font-family: sans-serif;}
                pre {margin: 0; font-family: monospace;}
                a:link {color: #009; text-decoration: none; background-color: #fff;}
                a:hover {text-decoration: underline;}
                table {border-collapse: collapse; border: 0; width: 100%; box-shadow: 1px 2px 3px #eee;}
                .center {text-align: center;}
                .center table {margin: 1em auto; text-align: left;}
                .center th {text-align: center !important;}
                td, th {border: 1px solid #aaa; font-size: 75%; vertical-align: baseline; padding: 4px 5px;}
                input {border: 1px solid #aaa; font-size: 100%; vertical-align: baseline; padding: 4px 5px;}
            </style>
        </head>    ';
    $table_body = "";
    for($i=0; $i<sizeof($arr); $i++ ) {
        if (!isset($arr[$i][$_GET['lang']])){
            $arr[$i][$_GET['lang']] = "";
        }
        $arr[$i][$_GET['lang']] =  str_replace('<button class="button" id="change_pass">', '__BUTTON', $arr[$i][$_GET['lang']]);
        $arr[$i][$_GET['lang']] =  str_replace('</button>', 'BUTTON__', $arr[$i][$_GET['lang']]);
        $table_body .= '<tr>';
        $table_body .= '<td>'.$i.'</td>';
        $table_body .= '<td>'.$arr[$i]['key'].'</td>';
        $table_body .= '<td>'.$arr[$i]['English'].'</td>';
        $table_body .= '<td>'.$arr[$i]['Korean'].'</td>';
        $table_body .= '<td><input type="text" name="'.$arr[$i]['key'].'" id= "'.$i.'" value="'.($arr[$i][$_GET['lang']]).'" onChange="edit_this(this)" size="100"></td>';
        $table_body .= '</tr>'."\r\n";
        
    }

    $table_body = '<table><tr><td>index</td><td>key</td><td>English</td><td>Korean</td><td>'.$_GET['lang'].'</td></tr>'.$table_body.'</table>';

    print $table_body;

echo '
    <script src="/js/jquery1.11.1.min.js"></script>
    <script src="/js/jqueryui.js"></script>
    <script>
    function edit_this(t){
        // console.log(t, t.id, t.name, t.value);
        url = "lang_json_edit.cgi?cat='.$_GET['cat'].'&mode=modify&lang='.$_GET['lang'].'&id=" + t.id + "&name=" + t.name + "&value=" + t.value ;
        console.log(url);
        var posting = $.post(url,{});
        posting.done(function(data) {
            console.log(data);
        });
    }
    </script>
';
}
?>
"""
