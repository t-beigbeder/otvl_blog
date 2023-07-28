echo $0 running $*
if [ -f /shell/custom_init.sh ] ; then
  exec /shell/custom_init.sh $*
fi
exec $*