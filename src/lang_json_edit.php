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
$input_tag_readonly = "";
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
    // print_r($arr_t);
    $json = json_encode($arr_t, JSON_PRETTY_PRINT);
    file_put_contents($filename, $json);
    // $arr = json_decode($json_body, true)['language'];
}
else if ($_GET['mode'] == 'delete'){
    // check if language is exist or not
    if (! isset($arr[0][$_GET['lang']])){
        print "Language: ".$_GET['lang']." not exisit";
        exit();
    }

    for($i=0; $i<sizeof($arr); $i++ ) {
        if (isset($arr[$i][$_GET['lang']])){
            unset($arr[$i][$_GET['lang']]);
        }
    }
    $arr_t['language'] = $arr;
    $json = json_encode($arr_t, JSON_PRETTY_PRINT);
    file_put_contents($filename, $json);
    $input_tag_readonly = "readonly";
}
else if ($_GET['mode'] == 'modify'){
    // print_r($_GET);
    file_put_contents($filename.'.bak', $json_body);
    $_GET['value'] =  str_replace('__BUTTON', '<button class="button" id="change_pass">', $_GET['value']);
    $_GET['value'] =  str_replace('BUTTON__', '</button>', $_GET['value']);

    $arr[$_GET['id']][$_GET['lang']] = $_GET['value'];
    $arr_t['language'] = $arr;
    $json = json_encode($arr_t, JSON_PRETTY_PRINT);
    file_put_contents($filename, $json);
    if ($_GET['cat'] == 'vca') {
        $json = json_encode($arr, JSON_PRETTY_PRINT);
        $json= substr($json, 1, strlen($json)-2);
        file_put_contents("/mnt/plugin/vca/web/pluginlang.json",$json);
    }
    // print $json;
    print "key: ".$_GET['name'].", ".$_GET['lang'].": ".$_GET['value']." is modified: OK";
    exit();
}

if ($_GET['mode'] != 'modify') {
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
        $table_body .= '<td><input type="text" name="'.$arr[$i]['key'].'" id= "'.$i.'" value="'.($arr[$i][$_GET['lang']]).'" onChange="edit_this(this)" size="100" '.$input_tag_readonly.'></td>';
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