INSTALL_DIR	= /var/lib/selfspy
DATA_DIR	= ~/.selfspy
SRCS		= activity_store.py password_dialog.py selfstats.py \
                  check_password.py period.py sniff_cocoa.py \
                  models.py selfspy.py sniff_x.py
all: install

install: copy $(DATA_DIR) /usr/bin/selfspy /usr/bin/selfstats

$(INSTALL_DIR):
	mkdir -p $@

$(DATA_DIR):
	mkdir -p $@

copy: $(SRCS) $(INSTALL_DIR)
	cp $(SRCS) $(INSTALL_DIR)

/usr/bin/selfspy:
	ln -s /var/lib/selfspy/selfspy.py $@

/usr/bin/selfstats:
	ln -s /var/lib/selfspy/selfstats.py $@
