#!/bin/sh
echo "################################################"
echo "### Enable Crond and Counting report service ###"
echo "### add crpt and hosted service setting menu ###"
echo "################################################"

CRONDIR="/var/spool/cron"
FILECRON="/var/spool/cron/crontabs/root"
STRCRPT="* * * * * /usr/bin/php-cgi -q /mnt/plugin/crpt/mk_ct_report.cgi"
STRTLSS="* * * * * /usr/bin/php-cgi -q /mnt/plugin/crpt/tlss.cgi"



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
    echo "$STRCRPT" > $FILECRON
fi

MODCRON=`cat $FILECRON | grep mk_ct_report.cgi | awk '{print $0}'`
# echo "$MODCRON"
if [ ! "$MODCRON" ] ;  then
    echo "appending string"
    echo "$STRCRPT" >> $FILECRON
fi

MODCRON=`cat $FILECRON | grep tlsst.cgi | awk '{print $0}'`
# echo "$MODCRON"
if [ ! "$MODCRON" ] ;  then
    echo "appending string"
    echo "$STRTLSS" >> $FILECRON
fi

ES=`ps -ef |grep crond | grep -v grep | awk '{print $1}'`
# echo "$ES"
if [ ! "$ES" ] ;  then
    echo "Service Crond start" 
    /usr/sbin/crond
fi

# sed -i'' -r -e "/Please Put it here/i\Some More Text is appended/" your_file.txt 
# sed -i'' -r -e "/Please Put it here/a\Some More Text is appended/" your_file.txt 
# sed -i'' -r -e "/<submenuname>advanced/i\<submenuname>counting_report</submenuname>\n<cgi>/cgi-bin/admin/vca/counting_report/setup_vca_crpt.cgi</cgi>" /tmp/plugin/plugin_info_list.xml
# sed -i'' -r -e "/<submenuname>advanced/i\<submenuname>hosted_service</submenuname>\n<cgi>/cgi-bin/admin/vca/hosted_service/setup_vca_hosted_service.cgi</cgi>" /tmp/plugin/plugin_info_list.xml



