# These files are binaries without symbols:
#
# makemkv-bin-%{version}/bin/amd64/makemkvcon
# makemkv-bin-%{version}/bin/i386/makemkvcon
# makemkv-bin-%{version}/bin/i386/mmdtsdec

# This is a binary image inserted in the compiled GUI binary:
# makemkv-oss-%{version}/makemkvgui/bin/image_data.bin

# mmdtsdec is a 32 bit only binary, so it is built only on i386 and required
# on x86_64.

%global _missing_build_ids_terminate_build 0

Summary:        DVD and Blu-ray to MKV converter and network streamer
Name:           makemkv
Version:        1.10.7
Release:        2%{?dist}
License:        GuinpinSoft inc and Mozilla Public License Version 1.1 and LGPLv2.1+
URL:            http://www.%{name}.com/
ExclusiveArch:  %{ix86} x86_64

Source0:        http://www.%{name}.com/download/%{name}-oss-%{version}.tar.gz
Source1:        http://www.%{name}.com/download/%{name}-bin-%{version}.tar.gz
Source2:        %{name}-changelog.txt
Source3:        %{name}.appdata.xml

BuildRequires:  desktop-file-utils
BuildRequires:  expat-devel
# Todo: unbundle these
#BuildRequires:  libebml-devel
#BuildRequires:  libmatroska-devel
#BuildRequires:  libmkv-devel
BuildRequires:  pkgconfig(libavcodec) >= 57
BuildRequires:  pkgconfig(libavutil) >= 55
BuildRequires:	qt4-devel

%if 0%{?fedora} >= 26 || 0%{?rhel} >= 8
BuildRequires:      compat-openssl10-devel
%else
BuildRequires:      openssl-devel
%endif

Requires:       hicolor-icon-theme
Requires:       mmdtsdec = %{version}-%{release}

%description
MakeMKV is your one-click solution to convert video that you own into free and
patents-unencumbered format that can be played everywhere. MakeMKV is a format
converter, otherwise called "transcoder".It converts the video clips from
proprietary (and usually encrypted) disc into a set of MKV files, preserving
most information but not changing it in any way. The MKV format can store
multiple video/audio tracks with all meta-information and preserve chapters.

Additionally MakeMKV can instantly stream decrypted video without intermediate
conversion to wide range of players, so you may watch Blu-ray and DVD discs with
your favorite player on your favorite OS or on your favorite device.

%ifarch %{ix86}
%package -n mmdtsdec
Summary:        MakeMKV DTS command line decoder

%description -n mmdtsdec
MakeMKV is your one-click solution to convert video that you own into free and
patents-unencumbered format that can be played everywhere. MakeMKV is a format
converter, otherwise called "transcoder".It converts the video clips from
proprietary (and usually encrypted) disc into a set of MKV files, preserving
most information but not changing it in any way. The MKV format can store
multiple video/audio tracks with all meta-information and preserve chapters.

This package contains the DTS decoder command line tool.
%endif

%prep
%setup -q -T -c -n %{name}-%{version} -a 0 -a 1
cp %{SOURCE2} .

%build
# Accept eula  
mkdir -p %{name}-bin-%{version}/tmp
echo "accepted" > %{name}-bin-%{version}/tmp/eula_accepted
cd %{name}-oss-%{version}
export CFLAGS="%{optflags} -D__GNU_SOURCE -D__STDC_CONSTANT_MACROS -D__STDC_LIMIT_MACROS -D __STDC_FORMAT_MACROS"
%configure --enable-debug
make %{?_smp_mflags}

%install
make -C %{name}-oss-%{version} install DESTDIR=%{buildroot} LIBDIR=%{_libdir}
make -C %{name}-bin-%{version} install DESTDIR=%{buildroot} LIBDIR=%{_libdir}
chmod 755 %{buildroot}%{_libdir}/lib*.so*
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

mkdir -p %{buildroot}%{_sysconfdir}/profile.d/

cat > %{buildroot}%{_sysconfdir}/profile.d/%{name}.sh <<EOF
export LIBBDPLUS_PATH=%{_libdir}/libmmbd.so.0
export LIBAACS_PATH=%{_libdir}/libmmbd.so.0
EOF

cat > %{buildroot}%{_sysconfdir}/profile.d/%{name}.csh <<EOF
setenv LIBBDPLUS_PATH %{_libdir}/libmmbd.so.0
setenv LIBAACS_PATH %{_libdir}/libmmbd.so.0
EOF

%if 0%{?fedora}
# Install AppData
mkdir -p %{buildroot}%{_datadir}/appdata
install -p -m 0644 %{SOURCE3} %{buildroot}%{_datadir}/appdata/
%endif

%ifarch x86_64
rm -f %{buildroot}/%{_bindir}/mmdtsdec
%endif

%post
%if 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
%endif
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
/sbin/ldconfig

%postun
%if 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
%endif
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
/sbin/ldconfig

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%license %{name}-bin-%{version}/src/eula_en_linux.txt
%license %{name}-oss-%{version}/License.txt
%doc %{name}-changelog.txt
%config(noreplace) %{_sysconfdir}/profile.d/%{name}.*sh
%{_bindir}/makemkv
%{_bindir}/makemkvcon
%{_datadir}/MakeMKV
%if 0%{?fedora}
%{_datadir}/appdata/%{name}.appdata.xml
%endif
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_libdir}/libdriveio.so.0
%{_libdir}/libmakemkv.so.1
%{_libdir}/libmmbd.so.0

%ifarch %{ix86}
%files -n mmdtsdec
%doc %{name}-bin-%{version}/src/eula_en_linux.txt
%{_bindir}/mmdtsdec
%endif

%changelog
* Thu Oct 26 2017 Simone Caronni <negativo17@gmail.com> - 1.10.7-2
- Update RPM macros.

* Sun Sep 10 2017 Simone Caronni <negativo17@gmail.com> - 1.10.7-1
- Update to 1.10.7.

* Mon Jul 17 2017 Simone Caronni <negativo17@gmail.com> - 1.10.6-2
- Use OpenSSL 1.0.x also on Fedora 26.

* Mon May 29 2017 Simone Caronni <negativo17@gmail.com> - 1.10.6-1
- Update to 1.10.6.

* Wed May 24 2017 Simone Caronni <negativo17@gmail.com> - 1.10.5-2
- Update compilation flags to support CentOS/RHEL 7.

* Mon Mar 27 2017 Simone Caronni <negativo17@gmail.com> - 1.10.5-1
- Update to 1.10.5, no-strip patch no longer required.

* Wed Jan 04 2017 Simone Caronni <negativo17@gmail.com> - 1.10.4-1
- Update to 1.10.4.
- Make sure FFmpeg compatibility libraries are not selected for building.

* Mon Dec 12 2016 Simone Caronni <negativo17@gmail.com> - 1.10.3-1
- Update to 1.10.3.

* Tue Oct 04 2016 Simone Caronni <negativo17@gmail.com> - 1.10.2-2
- Add AppStream metadata on Fedora 25+.
- Add missing update desktop database scriptlet for Fedora < 25 and RHEL.

* Mon Sep 19 2016 Simone Caronni <negativo17@gmail.com> - 1.10.2-1
- Update to 1.10.2.

* Thu Aug 11 2016 Simone Caronni <negativo17@gmail.com> - 1.10.1-1
- Update to 1.10.1.

* Thu Jul 21 2016 Simone Caronni <negativo17@gmail.com> - 1.10.0-1
- Update to 1.10.0.

* Tue Apr 19 2016 Simone Caronni <negativo17@gmail.com> - 1.9.10-1
- Update to 1.9.10.

* Mon Jan 18 2016 Simone Caronni <negativo17@gmail.com> - 1.9.9-1
- Update to 1.9.9.

* Mon Dec 21 2015 Simone Caronni <negativo17@gmail.com> - 1.9.8-1
- Update to 1.9.8.

* Mon Oct 05 2015 Simone Caronni <negativo17@gmail.com> - 1.9.7-1
- Update to 1.9.7.

* Mon Sep 28 2015 Simone Caronni <negativo17@gmail.com> - 1.9.6-1
- Update to 1.9.6.

* Tue Aug 18 2015 Simone Caronni <negativo17@gmail.com> - 1.9.5-2
- Create environment files for libbdplus and libaacs overriding.

* Wed Jul 29 2015 Simone Caronni <negativo17@gmail.com> - 1.9.5-1
- Update to 1.9.5.

* Fri Jun 19 2015 Simone Caronni <negativo17@gmail.com> - 1.9.4-1
- Update to version 1.9.4.
- Split out 32 bit only command mmdtsdec.
- Drop CentOS/RHEL 6 support.

* Wed Apr 08 2015 Simone Caronni <negativo17@gmail.com> - 1.9.2-1
- Update to 1.9.2.

* Mon Jan 26 2015 Simone Caronni <negativo17@gmail.com> - 1.9.1-1
- Update to 1.9.1.

* Thu Nov 20 2014 Simone Caronni <negativo17@gmail.com> - 1.9.0-1
- Update to 1.9.0.

* Fri Oct 24 2014 Simone Caronni <negativo17@gmail.com> - 1.8.14-1
- Update to 1.8.14.

* Mon Sep 08 2014 Simone Caronni <negativo17@gmail.com> - 1.8.13-1
- Update to 1.8.13.

* Thu Aug 21 2014 Simone Caronni <negativo17@gmail.com> - 1.8.12-1
- Update to 1.8.12.

* Mon Jun 23 2014 Simone Caronni <negativo17@gmail.com> - 1.8.11-1
- Update to 1.8.11.

* Thu Apr 17 2014 Simone Caronni <negativo17@gmail.com> - 1.8.10-1
- Update to 1.8.10.

* Fri Feb 28 2014 Simone Caronni <negativo17@gmail.com> - 1.8.9-1
- Updated to 1.8.9.
- Simplify configure line (now uses pkg-config).

* Thu Feb 06 2014 Simone Caronni <negativo17@gmail.com> - 1.8.8-2
- Actually package changelog.

* Wed Feb 05 2014 Simone Caronni <negativo17@gmail.com> - 1.8.8-1
- Update to 1.8.8.
- Added changelog.

* Mon Dec 30 2013 Simone Caronni <negativo17@gmail.com> - 1.8.7-2
- Add workaround for OpenSSL package not supplying required EC curves:
  https://bugzilla.redhat.com/show_bug.cgi?id=1042715#c7
  http://www.makemkv.com/forum2/viewtopic.php?f=3&t=7370&start=15#p31142

* Fri Dec 13 2013 Simone Caronni <negativo17@gmail.com> - 1.8.7-1
- Update to 1.8.7.
- Add debug package and compiler options.

* Thu Sep 19 2013 Simone Caronni <negativo17@gmail.com> - 1.8.5-1
- Update to 1.8.5.

* Mon Jul 22 2013 Simone Caronni <negativo17@gmail.com> - 1.8.4-2
- Update to 1.8.4.
- Removed EPEL 5 support, QT too old.

* Thu May 30 2013 Simone Caronni <negativo17@gmail.com> - 1.8.3-1
- Updated to 1.8.3.

* Tue May 21 2013 Simone Caronni <negativo17@gmail.com> - 1.8.2-1
- Update to 1.8.2.

* Wed May 01 2013 Simone Caronni <negativo17@gmail.com> - 1.8.2-2
- Check desktop file during %%install.

* Wed May 01 2013 Simone Caronni <negativo17@gmail.com> - 1.8.2-1
- First build.
