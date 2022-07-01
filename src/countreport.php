<?
$fname = "/mnt/plugin/crpt/crpt.ini";
if (!file_exists($fname)) {
    Header('Content-type: text/txt; charset=UTF-8');
	print "No config file";
	exit();
}
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
//validate Get param
foreach($_GET as $key=>$val){
    $_GET[$key] = strtolower($val);
}
// print_r($_GET);
function popupHelp(){
    Header('Content-type: text/txt; charset=UTF-8');
    $str = ''.
        'countreport.cgi?{PARAMETERS}'.PHP_EOL.PHP_EOL.
        'reportfmt: report format, [csv, table, json, chart]'.PHP_EOL.
        'sampling: sampling interval, secs, 60 is 1 minute, must be integer and multiplied by 60.'.PHP_EOL.
        'table: db table [0~4], ethier one in [sampling and table]'.PHP_EOL.
        'order: order in data, [asc, desc]'.PHP_EOL.
        'value: count value, absolute value or difference value [abs, diff] '.PHP_EOL.
        'from: start date YYYY/MM/DD [HH:MM:SS] or [yesterday, today, now, thisweek, thismonth, lastweek, lastmonth] '.PHP_EOL.
        'to: end date  YYYY/MM/DD [HH:MM:SS] or [yesterday, today, now, thisweek, thismonth, lastweek, lastmonth] ';
    print $str;
    exit();

}
if (!isset($_GET['from']) || !isset($_GET['to'])) {
    popupHelp();
}
if ( !isset($_GET['reportfmt']) || !in_array($_GET['reportfmt'], ['csv', 'table', 'json','chart'])){
    popupHelp();
 }
if (!isset($_GET['order']) || !in_array($_GET['order'], ['asc', 'ascending', 'desc','descending'])){
    popupHelp();
}
if (isset($_GET['sampling'])){
    if( (strval(intval($_GET['sampling'])) !=  strval($_GET['sampling'])) || ($_GET['sampling']%60 !=0) ) {
        popupHelp();
    }
    for($i=0; $i<4; $i++){
        if ($config['table'.$i.'.interval'] == $_GET['sampling']) {
            $filedb = "/mnt/plugin/.config/vca-cored/configuration/countreport.table".$i.".db";
            break;
        }
    }
}
else if(isset($_GET['table'])){
    $filedb = "/mnt/plugin/.config/vca-cored/configuration/countreport.table".$_GET['table'].".db";
    if (!is_file($filedb)) {
        print ("<br>Error: db_file countreport.table".$_GET['table'].".db not exist" );
        exit();
    }
}
if (!isset($_GET['value']) || !in_array($_GET['value'], ['abs', 'diff'])){
    popupHelp();
}
// print $filedb;

require('/root/web/cgi-bin/_define.inc');
require('/root/web/cgi-bin/class/system.class');
$shm_id = shmop_open(KEY_SM_SHARED_CONFIG, "a", 0, 0);
$system_conf = new CSystemConfiguration($shm_id);
shmop_close($shm_id);
$TimezoneIndex = $system_conf->SystemDatetime->TimeZoneIndex;
$timezone = "Etc/GMT".($TimezoneIndex-12 >0 ? "-".strval($TimezoneIndex-12): "+".strval(12-$TimezoneIndex));
date_default_timezone_set($timezone);

function datestrtotime($str){
    $arr = ['yesterday', 'today', 'now', "thisweek", "thismonth", "lastweek", "lastmonth"];
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
    // $ts = strtotime(date("Y-m-d H:i:00", $ts));
    $ts = ceil($ts/60)*60;
    return $ts;
}



function getDB($filedb){
    $from_ts = datestrtotime($_GET['from']);
    $to_ts = datestrtotime($_GET['to']);
    
    $ct_names =array();
    $counters = array();
    $db_body = file_get_contents($filedb);
    $arr = json_decode($db_body, true);
    if (!$arr){
        $arr = array();
    }

    $pre_val = array();
    foreach($arr as $arr_rs){
        // print $from_ts."   ".strtotime($arr_rs['datetime'])."    ".$to_ts."\n";
        
        if (strtotime($arr_rs['datetime']) <$from_ts) {
            continue;
        }
        else if(strtotime($arr_rs['datetime']) > $to_ts) {
            continue;
        }

        foreach($arr_rs['counters'] as $ct){
            if (!in_array($ct['name'],$ct_names)) {
                array_push($ct_names, $ct['name']);
            }
            if($_GET['value'] == 'diff') {
                if (!isset($prev_val[$ct['name']])){
                    $prev_val[$ct['name']]= $ct['value'];
                }
                $counters[$arr_rs['datetime']][$ct['name']] =  $ct['value'] - $prev_val[$ct['name']];
                $prev_val[$ct['name']] = $ct['value'];
            }
            else {
                $counters[$arr_rs['datetime']][$ct['name']] = $ct['value'];
            }
        }
    }
    return ["ct_names"=>$ct_names, "data"=>$counters];
}
$arr = getDB($filedb);
if ($_GET['order'] == 'desc' || $_GET['order'] == 'descending'){
    $arr['data'] = array_reverse($arr['data']);
}
// print_r($arr);

if ($_GET['reportfmt'] == 'json'){
    Header('Content-type: text/json; charset=UTF-8');
    print json_encode($arr['data'], JSON_PRETTY_PRINT);
    exit();
}
else if ($_GET['reportfmt'] == 'table'){
    Header('Content-type: text/html; charset=UTF-8');
    $records = sizeof($arr['data']);
    $table_body = PHP_EOL.'<tr><td>'."Records:".$records." Counter:".sizeof($arr['ct_names']).'</td>';
    $i=0;
    foreach($arr['ct_names'] as $ct_name){
        $table_body .= '<td>'.($i++).":".$ct_name.'</td>';
    }
    $table_body .= '</tr>';    

    foreach($arr['data'] as $datetime => $counts){
        $table_body .= PHP_EOL.'<tr><td>'.$datetime.'</td>';
        foreach($arr['ct_names'] as $ct_name){
            if (!isset($counts[$ct_name])){
                $counts[$ct_name] = 0;
            }
            $table_body .= '<td>'.$counts[$ct_name].'</td>';
        }
        $table_body .= '</tr>';
    }    
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
    $fname = "count_".time().".csv";
    // Header('Content-type: text/csv; charset=UTF-8');
    // header("Content-Disposition:attachment;filename=$fname");
    $records = sizeof($arr['data']);
    $table_body = "Records:".$records." Counter:".sizeof($arr['ct_names']);
    $i=0;
    foreach($arr['ct_names'] as $ct_name){
        $table_body .= ','.($i++).":".$ct_name;
    }
    foreach($arr['data'] as $datetime => $counts){
        $table_body .= PHP_EOL.$datetime;
        foreach($arr['ct_names'] as $ct_name){
            $table_body .= ','.$counts[$ct_name];
        }
    }
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
    foreach($arr['ct_names'] as $ct_name){
        $arr_d[$ct_name] = array();
    }
    foreach($arr['data'] as $datetime => $counts){
        array_push($arr_ts, $datetime);
        foreach($counts as $ct_name => $val){
            array_push($arr_d[$ct_name], $val);
        }
    }
    // print_r($arr_d);
    foreach($arr['ct_names'] as $ct_name){
        $rand_color = array_shift($arr_wcolor);
        array_push($arr_t, [
            'label'=> $ct_name, 
            'data' => $arr_d[$ct_name], 
            'borderWidth'=>1, 
            'borderColor'=>$rand_color, 
            'backgroundColor'=>$rand_color, 
            'fill'=>false, 
            'tension'=>0.5
        ]);
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
    exit();
}

// $start = $arr[0]['timestamp'];
// $last  = $arr[sizeof($arr)-1]['timestamp'];

exit();

?>