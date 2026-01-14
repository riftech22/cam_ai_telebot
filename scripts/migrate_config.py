#!/usr/bin/env python3
"""
Migrate config.yaml from old format to new format
Script ini otomatis mengubah konfigurasi lama ke format baru
"""

import yaml
import sys
from pathlib import Path


def migrate_config(config_path):
    """
    Migrasi config.yaml dari format lama ke format baru
    
    Args:
        config_path: Path ke config.yaml
    """
    print("📝 Membaca config lama...")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    changes = []
    
    # 1. Update detection interval
    if 'detection' in config:
        if 'detection_interval' not in config['detection']:
            config['detection']['detection_interval'] = 2
            changes.append("✅ Tambahkan detection_interval: 2")
        elif config['detection']['detection_interval'] == 2:
            config['detection']['detection_interval'] = 1
            changes.append("✅ Update detection_interval: 2 → 1 (real-time)")
        
        # Tambahkan motion_detection_enabled
        if 'motion_detection_enabled' not in config['detection']:
            config['detection']['motion_detection_enabled'] = True
            changes.append("✅ Tambahkan motion_detection_enabled: true")
    
    # 2. Tambahkan motion_detection section
    if 'motion_detection' not in config:
        config['motion_detection'] = {
            'min_contour_area': 500,
            'sensitivity': 25,
            'cooldown_seconds': 2,
            'min_motion_percentage': 2
        }
        changes.append("✅ Tambahkan section motion_detection")
    else:
        # Update motion_detection cooldown
        if 'cooldown_seconds' in config['motion_detection']:
            if config['motion_detection']['cooldown_seconds'] > 2:
                old = config['motion_detection']['cooldown_seconds']
                config['motion_detection']['cooldown_seconds'] = 2
                changes.append(f"✅ Update motion_detection.cooldown_seconds: {old} → 2 (real-time)")
    
    # 3. Update notification section
    if 'notification' in config:
        notif = config['notification']
        
        # Ubah send_photo → send_on_motion
        if 'send_photo' in notif and 'send_on_motion' not in notif:
            notif['send_on_motion'] = notif['send_photo']
            del notif['send_photo']
            changes.append("✅ Ubah send_photo → send_on_motion")
        
        # Ubah alert_on_known → send_on_person
        if 'alert_on_known' in notif and 'send_on_person' not in notif:
            notif['send_on_person'] = notif['alert_on_known']
            del notif['alert_on_known']
            changes.append("✅ Ubah alert_on_known → send_on_person")
        
        # Ubah alert_on_unknown → send_on_unknown_face
        if 'alert_on_unknown' in notif and 'send_on_unknown_face' not in notif:
            notif['send_on_unknown_face'] = notif['alert_on_unknown']
            del notif['alert_on_unknown']
            changes.append("✅ Ubah alert_on_unknown → send_on_unknown_face")
        
        # Tambahkan person_detection_cooldown
        if 'person_detection_cooldown' not in notif:
            notif['person_detection_cooldown'] = 5
            changes.append("✅ Tambahkan person_detection_cooldown: 5 (real-time)")
        elif notif['person_detection_cooldown'] > 5:
            old = notif['person_detection_cooldown']
            notif['person_detection_cooldown'] = 5
            changes.append(f"✅ Update person_detection_cooldown: {old} → 5 (real-time)")
        
        # Tambahkan duplicate_threshold_seconds (PENTING!)
        if 'duplicate_threshold_seconds' not in notif:
            notif['duplicate_threshold_seconds'] = 5
            changes.append("✅ Tambahkan duplicate_threshold_seconds: 5 (mencegah duplicate)")
        
        # Tambahkan include_motion_mask
        if 'include_motion_mask' not in notif:
            notif['include_motion_mask'] = False
            changes.append("✅ Tambahkan include_motion_mask: false")
    
    # 4. Pindahkan quiet_hours ke notification
    if 'quiet_hours' in config:
        if 'notification' in config:
            config['notification']['quiet_hours'] = config['quiet_hours']
        del config['quiet_hours']
        changes.append("✅ Pindahkan quiet_hours ke notification section")
    
    # Print semua perubahan
    print("\n" + "="*60)
    print("📋 PERUBAHAN YANG DILAKUKAN:")
    print("="*60)
    if changes:
        for change in changes:
            print(change)
    else:
        print("ℹ️  Config sudah dalam format terbaru, tidak ada perubahan")
    print("="*60)
    
    # Backup config lama
    backup_path = config_path.with_suffix('.yaml.backup')
    print(f"\n💾 Backup config lama ke: {backup_path}")
    
    with open(backup_path, 'w') as f:
        with open(config_path, 'r') as f_backup:
            f.write(f_backup.read())
    
    # Simpan config baru
    print(f"💾 Simpan config baru ke: {config_path}")
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print("\n✅ Migrasi config berhasil!")
    print("\n🔄 Restart service untuk menerapkan perubahan:")
    print("   sudo systemctl restart cctv-ai-bot")
    
    return changes


def main():
    """Fungsi main"""
    print("="*60)
    print("🔄 MIGRASI CONFIG.YAML - OTOMATIS")
    print("="*60)
    print()
    
    # Cek path config
    possible_paths = [
        Path("/opt/cam_ai_telebot/config/config.yaml"),
        Path("./config/config.yaml"),
        Path("../config/config.yaml"),
    ]
    
    config_path = None
    for path in possible_paths:
        if path.exists():
            config_path = path
            break
    
    if config_path is None:
        print("❌ Error: config.yaml tidak ditemukan!")
        print("   Cek path:")
        for path in possible_paths:
            print(f"   - {path}")
        sys.exit(1)
    
    print(f"📁 Config ditemukan di: {config_path}")
    print()
    
    # Konfirmasi
    print("⚠️  Script ini akan mengubah config.yaml")
    print("   Backup akan dibuat otomatis sebagai config.yaml.backup")
    print()
    response = input("Lanjutkan? (y/N): ")
    
    if response.lower() != 'y':
        print("❌ Dibatalkan oleh user")
        sys.exit(0)
    
    print()
    
    # Migrasi
    try:
        changes = migrate_config(config_path)
        
        if changes:
            print()
            print("🎯 SUMMARY:")
            print(f"   Total perubahan: {len(changes)}")
            print()
            print("📝 Perubahan penting:")
            for change in changes:
                if "real-time" in change.lower() or "duplicate" in change.lower():
                    print(f"   - {change}")
        
        print()
        print("="*60)
        print("✅ MIGRASI SELESAI")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error saat migrasi: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
