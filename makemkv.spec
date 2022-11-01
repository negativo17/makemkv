# These files are binaries without symbols:
#
# makemkv-bin-%{version}/bin/amd64/makemkvcon
# makemkv-bin-%{version}/bin/i386/makemkvcon

# This is a binary image inserted in the compiled GUI binary:
# makemkv-oss-%{version}/makemkvgui/bin/image_data.bin

# mmdtsdec is a 32 bit only binary, so it is built only on i386 and required
# on x86_64.

%global _missing_build_ids_terminate_build 0

Summary:        DVD and Blu-ray to MKV converter and network streamer
Name:           makemkv
Version:        1.17.2
Release:        1%{?dist}
License:        GuinpinSoft inc and Mozilla Public License Version 1.1 and LGPLv2.1+
URL:            http://www.%{name}.com/
ExclusiveArch:  %{ix86} x86_64 aarch64 armv7hl

Source0:        http://www.%{name}.com/download/%{name}-oss-%{version}.tar.gz
Source1:        http://www.%{name}.com/download/%{name}-bin-%{version}.tar.gz
Source2:        changelog.txt
Source3:        %{name}.appdata.xml
Source4:        http://www.%{name}.com/developers/usage.txt#/%{name}con.txt

BuildRequires:  desktop-file-utils
BuildRequires:  expat-devel
# Todo: unbundle these
#BuildRequires:  libebml-devel
#BuildRequires:  libmatroska-devel
#BuildRequires:  libmkv-devel
BuildRequires:  openssl-devel
# Specify minimum version so looks for latest FFMpeg
BuildRequires:  pkgconfig(libavcodec) >= 58
BuildRequires:  pkgconfig(libavutil) >= 56
BuildRequires:	pkgconfig(Qt5Core)
BuildRequires:	pkgconfig(Qt5Gui)
BuildRequires:	pkgconfig(Qt5Widgets)
BuildRequires:	pkgconfig(Qt5DBus)
BuildRequires:  zlib-devel

%if 0%{?rhel} == 7
BuildRequires:  devtoolset-8-gcc-c++
%else
BuildRequires:  gcc-c++
%endif

Requires:       hicolor-icon-theme

# This makes sure you can open AACS and BD+ encrypted BluRays transparently.
# See below in the install section.
Provides:       libaacs%{?_isa} = %{version}-%{release}
Provides:       libbdplus%{?_isa} = %{version}-%{release}
Obsoletes:      libaacs < %{version}-%{release}
Obsoletes:      libbdplus < %{version}-%{release}

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

%prep
%setup -q -T -c -n %{name}-%{version} -a 0 -a 1
cp %{SOURCE2} %{SOURCE4} .

%build
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-8/enable
%endif

# Accept eula  
mkdir -p %{name}-bin-%{version}/tmp
echo "accepted" > %{name}-bin-%{version}/tmp/eula_accepted

cd %{name}-oss-%{version}
export CFLAGS="%{optflags} -D__GNU_SOURCE -D__STDC_CONSTANT_MACROS -D__STDC_LIMIT_MACROS -D __STDC_FORMAT_MACROS"
%configure --enable-debug --enable-allcodecs
make %{?_smp_mflags}

%install
make -C %{name}-oss-%{version} install DESTDIR=%{buildroot} LIBDIR=%{_libdir}
make -C %{name}-bin-%{version} install DESTDIR=%{buildroot} LIBDIR=%{_libdir}
chmod 755 %{buildroot}%{_libdir}/lib*.so*

# Transparenty enable AACS and BD+ decryption, libbluray supports overriding
# libaacs and libbdplus.
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

%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

%post
%if 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
%endif
%{?ldconfig}

%postun
%if 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
%endif
%{?ldconfig}

%if 0%{?rhel} == 7
%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
%endif

%files
%license %{name}-bin-%{version}/src/eula_en_linux.txt
%license %{name}-oss-%{version}/License.txt
%doc changelog.txt makemkvcon.txt
%config(noreplace) %{_sysconfdir}/profile.d/%{name}.*sh
%{_bindir}/makemkv
%{_bindir}/makemkvcon
%{_bindir}/mmccextr
%{_bindir}/mmgplsrv
%{_bindir}/sdftool
%{_datadir}/MakeMKV
%if 0%{?fedora}
%{_datadir}/appdata/%{name}.appdata.xml
%endif
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_libdir}/libdriveio.so.0
%{_libdir}/libmakemkv.so.1
%{_libdir}/libmmbd.so.0

%changelog
* Tue Nov 01 2022 Simone Caronni <negativo17@gmail.com> - 1.17.2-1
- Update to 1.17.2.

* Thu Jul 14 2022 Simone Caronni <negativo17@gmail.com> - 1.17.1-1
- Update to 1.17.1.

* Tue Jul 05 2022 Simone Caronni <negativo17@gmail.com> - 1.17.0-1
- Update to 1.17.0.
- Trim changelog.

* Wed Apr 06 2022 Simone Caronni <negativo17@gmail.com> - 1.16.7-3
- Rebuild for updated dependencies.

* Wed Apr 06 2022 Simone Caronni <negativo17@gmail.com> - 1.16.7-2
- Rebuild for updated dependencies.

* Tue Mar 01 2022 Simone Caronni <negativo17@gmail.com> - 1.16.7-1
- Update to 1.16.7.

* Tue Nov 02 2021 Simone Caronni <negativo17@gmail.com> - 1.16.5-1
- Update to 1.16.5.

* Tue Jul 20 2021 Simone Caronni <negativo17@gmail.com> - 1.16.4-1
- Update to 1.16.4.

* Fri Mar 26 2021 Simone Caronni <negativo17@gmail.com> - 1.16.3-1
- Update to 1.16.3.
- Remove ccextractor dependency, mmccextr is a bundled stripped down version.

* Mon Mar 15 2021 Simone Caronni <negativo17@gmail.com> - 1.16.1-1
- Update to 1.16.1.

* Thu Dec 17 2020 Simone Caronni <negativo17@gmail.com> - 1.15.4-1
- Update to 1.15.4.

* Mon Oct 12 2020 Simone Caronni <negativo17@gmail.com> - 1.15.3-1
- Update to 1.15.3.

* Mon Aug 17 2020 Simone Caronni <negativo17@gmail.com> - 1.15.2-1
- Update to 1.15.2.

* Fri Apr 24 2020 Simone Caronni <negativo17@gmail.com> - 1.15.1-1
- Update to 1.15.1.

* Sat Mar 07 2020 Simone Caronni <negativo17@gmail.com> - 1.15.0-1
- Update to 1.15.0.
