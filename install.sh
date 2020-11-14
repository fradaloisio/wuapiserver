virtualenv --python=/usr/bin/python3 venv
if [ $? != 0 ];then
   pip3 install --user virtualenv
   virtualenv --python=/usr/bin/python3 venv
fi
source venv/bin/activate
pip3 install -r requirements.txt