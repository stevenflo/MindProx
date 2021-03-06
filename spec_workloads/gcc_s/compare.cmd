-E DERBY_HOME /usr/lib/jvm/java-8-oracle/db
-E HOME /home/rpanda
-E J2REDIR /usr/lib/jvm/java-8-oracle/jre
-E J2SDKDIR /usr/lib/jvm/java-8-oracle
-E JAVA_HOME /usr/lib/jvm/java-8-oracle
-E LANG en_US.UTF-8
-E LC_ALL C
-E LC_LANG C
-E LD_LIBRARY_PATH /usr/lib/gcc/x86_64-linux-gnu/4.8/:/usr/lib64/:/usr/lib/:/lib64
-E LESSCLOSE '/usr/bin/lesspipe %s %s'
-E LESSOPEN '| /usr/bin/lesspipe %s'
-E LIBC_FATAL_STDERR_ 1
-E LOGNAME rpanda
-E LS_COLORS 'rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arj=01;31:*.taz=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.zip=01;31:*.z=01;31:*.Z=01;31:*.dz=01;31:*.gz=01;31:*.lz=01;31:*.xz=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.jpg=01;35:*.jpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.axv=01;35:*.anx=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.axa=00;36:*.oga=00;36:*.spx=00;36:*.xspf=00;36:'
-E MAIL /var/mail/rpanda
-E OLDPWD /home/rpanda/spec-clustering/cpu2017
-E OMP_NUM_THREADS 1
-E OMP_THREAD_LIMIT 1
-E PATH /home/rpanda/spec-clustering/cpu2017/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/jvm/java-8-oracle/bin:/usr/lib/jvm/java-8-oracle/db/bin:/usr/lib/jvm/java-8-oracle/jre/bin
-E SHELL /bin/bash
-E SPEC /home/rpanda/spec-clustering/cpu2017
-E SPECDB_PWD /home/rpanda/spec-clustering/cpu2017/config
-E SPECPERLLIB /home/rpanda/spec-clustering/cpu2017/bin/lib:/home/rpanda/spec-clustering/cpu2017/bin
-E SSH_CLIENT '10.146.252.16 65389 3131'
-E SSH_CONNECTION '10.146.252.16 65389 129.116.238.140 3131'
-E SSH_TTY /dev/pts/2
-E TERM xterm
-E USER rpanda
-E XDG_RUNTIME_DIR /run/user/1001
-E XDG_SESSION_ID 169
-r
-N C
-C /home/rpanda/spec-clustering/cpu2017/benchspec/CPU/602.gcc_s/run/run_base_refspeed_gcc48-64bit-m64.0000
-k -o gcc-pp.opts-O5_-finline-limit_1000_-fselective-scheduling_-fselective-scheduling2.s.cmp /home/rpanda/spec-clustering/cpu2017/bin/specperl /home/rpanda/spec-clustering/cpu2017/bin/harness/specdiff -m -l 10 --floatcompare --nonansupport /home/rpanda/spec-clustering/cpu2017/benchspec/CPU/502.gcc_r/data/refspeed/output/gcc-pp.opts-O5_-finline-limit_1000_-fselective-scheduling_-fselective-scheduling2.s gcc-pp.opts-O5_-finline-limit_1000_-fselective-scheduling_-fselective-scheduling2.s > gcc-pp.opts-O5_-finline-limit_1000_-fselective-scheduling_-fselective-scheduling2.s.cmp
-k -o gcc-pp.opts-O5_-finline-limit_24000_-fgcse_-fgcse-las_-fgcse-lm_-fgcse-sm.s.cmp /home/rpanda/spec-clustering/cpu2017/bin/specperl /home/rpanda/spec-clustering/cpu2017/bin/harness/specdiff -m -l 10 --floatcompare --nonansupport /home/rpanda/spec-clustering/cpu2017/benchspec/CPU/502.gcc_r/data/refspeed/output/gcc-pp.opts-O5_-finline-limit_24000_-fgcse_-fgcse-las_-fgcse-lm_-fgcse-sm.s gcc-pp.opts-O5_-finline-limit_24000_-fgcse_-fgcse-las_-fgcse-lm_-fgcse-sm.s > gcc-pp.opts-O5_-finline-limit_24000_-fgcse_-fgcse-las_-fgcse-lm_-fgcse-sm.s.cmp
-k -o gcc-pp.opts-O5_-fipa-pta.s.cmp /home/rpanda/spec-clustering/cpu2017/bin/specperl /home/rpanda/spec-clustering/cpu2017/bin/harness/specdiff -m -l 10 --floatcompare --nonansupport /home/rpanda/spec-clustering/cpu2017/benchspec/CPU/502.gcc_r/data/refspeed/output/gcc-pp.opts-O5_-fipa-pta.s gcc-pp.opts-O5_-fipa-pta.s > gcc-pp.opts-O5_-fipa-pta.s.cmp
