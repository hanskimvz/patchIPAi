#!/bin/sh

PLUGIN_DIR="/mnt/plugin"
PLUGIN_TMPDIR="/tmp/plugin"
IPNC_WEPDIR="/root/web"

PLUGIN_LIST=`ls -l ${PLUGIN_DIR}/ | grep ^d | awk '{print $9}'`
INFO_FILE="web/info.dat"
INFO_LIST_FILE="plugin_info_list.xml"

#echo "$PLUGIN_LIST"
#make plugin_info_list.xml file
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" > ${PLUGIN_TMPDIR}/${INFO_LIST_FILE}
echo "<plugin_list>" >> ${PLUGIN_TMPDIR}/${INFO_LIST_FILE}

for LIST in ${PLUGIN_LIST} ;do
  if [ -f ${PLUGIN_DIR}/${LIST}/${INFO_FILE} ]; then
    cat ${PLUGIN_DIR}/${LIST}/${INFO_FILE} >> ${PLUGIN_TMPDIR}/${INFO_LIST_FILE}
  fi
done

echo "</plugin_list>" >> ${PLUGIN_TMPDIR}/${INFO_LIST_FILE}
#link plugin tmp dir to ipnc web dir
ln -s ${PLUGIN_TMPDIR}/${INFO_LIST_FILE} ${IPNC_WEPDIR}/${INFO_LIST_FILE}

#make plugin_cgilist.conf file
PLUGIN_CGI_CONF_FILE="plugin_cgi.conf"
PLUGIN_CGI_LIST_CONF_FILE="plugin_cgilist.conf"

rm -rf ${PLUGIN_TMPDIR}/${PLUGIN_CGI_LIST_CONF_FILE}
touch ${PLUGIN_TMPDIR}/${PLUGIN_CGI_LIST_CONF_FILE}
for LIST in ${PLUGIN_LIST} ;do
  if [ -f ${PLUGIN_DIR}/${LIST}/web/${PLUGIN_CGI_CONF_FILE} ]; then
    cat ${PLUGIN_DIR}/${LIST}/web/${PLUGIN_CGI_CONF_FILE} >> ${PLUGIN_TMPDIR}/${PLUGIN_CGI_LIST_CONF_FILE}
  fi
done

if [ ! -L ${PLUGIN_DIR}/${PLUGIN_CGI_LIST_CONF_FILE} ]; then
    rm -rf ${PLUGIN_DIR}/${PLUGIN_CGI_LIST_CONF_FILE}
    ln -s  ${PLUGIN_TMPDIR}/${PLUGIN_CGI_LIST_CONF_FILE} ${PLUGIN_DIR}/${PLUGIN_CGI_LIST_CONF_FILE}
fi

#make plugin_web.conf file
PLUGIN_WEB_CONF_FILE="plugin_web.conf"

rm -rf ${PLUGIN_TMPDIR}/${PLUGIN_WEB_CONF_FILE}
touch ${PLUGIN_TMPDIR}/${PLUGIN_WEB_CONF_FILE}
for LIST in ${PLUGIN_LIST} ;do
  if [ -f ${PLUGIN_DIR}/${LIST}/web/${PLUGIN_WEB_CONF_FILE} ]; then
    cat ${PLUGIN_DIR}/${LIST}/web/${PLUGIN_WEB_CONF_FILE} >> ${PLUGIN_TMPDIR}/${PLUGIN_WEB_CONF_FILE}
  fi
done

if [ ! -L ${PLUGIN_DIR}/${PLUGIN_WEB_CONF_FILE} ]; then
    rm -rf ${PLUGIN_DIR}/${PLUGIN_WEB_CONF_FILE}
    ln -s  ${PLUGIN_TMPDIR}/${PLUGIN_WEB_CONF_FILE} ${PLUGIN_DIR}/${PLUGIN_WEB_CONF_FILE}
fi

#make set iptable script file
#PLUGIN_IPTABLE_SCRIPT="plugin_iptable.sh"

#echo "iptables -D CPRO_POLICY -s 127.0.0.1 -j ACCEPT" > ${PLUGIN_DIR}/${PLUGIN_IPTABLE_SCRIPT}
#echo "iptables -I CPRO_POLICY -s 127.0.0.1 -j ACCEPT" >> ${PLUGIN_DIR}/${PLUGIN_IPTABLE_SCRIPT}
#chmod 777 ${PLUGIN_DIR}/${PLUGIN_IPTABLE_SCRIPT}
#for LIST in ${PLUGIN_LIST} ;do
#  if [ -f ${PLUGIN_DIR}/${LIST}/script/${PLUGIN_IPTABLE_SCRIPT} ]; then
#    cat ${PLUGIN_DIR}/${LIST}/script/${PLUGIN_IPTABLE_SCRIPT} >> ${PLUGIN_DIR}/${PLUGIN_IPTABLE_SCRIPT}
#  fi
#done

#make pluginlang.json file
PLUGIN_LANG_JSON_FILE="pluginlang.json"

echo "{" > ${PLUGIN_TMPDIR}/${PLUGIN_LANG_JSON_FILE}
echo "  \"language\": [" >> ${PLUGIN_TMPDIR}/${PLUGIN_LANG_JSON_FILE}

_cnt=0
for LIST in ${PLUGIN_LIST} ;do
  if [ -f ${PLUGIN_DIR}/${LIST}/web/${PLUGIN_LANG_JSON_FILE} ]; then
    if [ "$_cnt" -ge "1" ]; then
      echo "," >> ${PLUGIN_TMPDIR}/${PLUGIN_LANG_JSON_FILE}
    fi
    cat ${PLUGIN_DIR}/${LIST}/web/${PLUGIN_LANG_JSON_FILE} >> ${PLUGIN_TMPDIR}/${PLUGIN_LANG_JSON_FILE}
    _cnt=$(($_cnt+1))
  fi
done
echo "  ]" >> ${PLUGIN_TMPDIR}/${PLUGIN_LANG_JSON_FILE}
echo "}" >> ${PLUGIN_TMPDIR}/${PLUGIN_LANG_JSON_FILE}

if [ ! -L ${IPNC_WEPDIR}/js/${PLUGIN_LANG_JSON_FILE} ]; then
    rm -rf ${IPNC_WEPDIR}/js/${PLUGIN_LANG_JSON_FILE}
    ln -s ${PLUGIN_TMPDIR}/${PLUGIN_LANG_JSON_FILE} ${IPNC_WEPDIR}/js/${PLUGIN_LANG_JSON_FILE}
fi

#link plugin_user_event_index.txt
if [ ! -L ${IPNC_WEPDIR}/plugin_user_event_index.txt ]; then
    rm -rf ${IPNC_WEPDIR}/plugin_user_event_index.txt
    ln -s ${PLUGIN_DIR}/.config/plugin_user_event_index.txt ${IPNC_WEPDIR}/plugin_user_event_index.txt
fi
#link plugin_user_event_index_ext.txt
if [ ! -L ${IPNC_WEPDIR}/plugin_user_event_index_ext.txt ]; then
    rm -rf ${IPNC_WEPDIR}/plugin_user_event_index_ext.txt
    ln -s ${PLUGIN_DIR}/.config/plugin_user_event_index_ext.txt ${IPNC_WEPDIR}/plugin_user_event_index_ext.txt
fi



sed -i'' -r -e "/<submenuname>advanced/i\<submenuname>counting_report</submenuname>\n<cgi>/cgi-bin/admin/vca/counting_report/setup_vca_crpt.cgi</cgi>" /tmp/plugin/plugin_info_list.xml
sed -i'' -r -e "/<submenuname>advanced/i\<submenuname>hosted_service</submenuname>\n<cgi>/cgi-bin/admin/vca/hosted_service/setup_vca_hosted_service.cgi</cgi>" /tmp/plugin/plugin_info_list.xml