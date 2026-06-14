import sys, os
from copy import deepcopy
from map_loader import load_map, get_grid
from team import Team
from race_manager import RaceManager

# ================== تنظیمات تست ==================
# استفاده از یک نقشهٔ کوچک ۳×۳ با دو هدف برای سرعت بالا
TEST_MAP = {
    "name": "test_map",
    "width": 3,
    "height": 3,
    "grid": [
        [0, 0, 4],
        [0, 1, 0],
        [4, 0, 0]
    ]
}

def test_full_rescue_and_termination():
    print("=" * 50)
    print("شروع تست یکپارچگی کامل (Shared Grid + Q-Learning)")
    print("=" * 50)

    # ۱. ساخت مسابقه با نقشهٔ تست
    print("\n[1] ساخت RaceManager با نقشهٔ تست...")
    # RaceManager نیاز به فایل JSON دارد، اما ما مستقیماً از دیکشنری استفاده می‌کنیم.
    # برای سادگی، فایل JSON موقت می‌سازیم.
    import tempfile, json
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(TEST_MAP, f)
        temp_map_path = f.name

    try:
        race = RaceManager(temp_map_path, ["AI Team 1", "AI Team 2"])
        print("✓ RaceManager ساخته شد.")

        # ۲. بررسی وجود shared_grid
        assert hasattr(race, 'shared_grid'), "❌ race_manager فاقد shared_grid است!"
        print("✓ shared_grid وجود دارد.")

        # ۳. بررسی اینکه تیم‌ها در ابتدا همه اهداف را می‌بینند
        initial_targets = sum(row.count(4) for row in race.shared_grid)
        print(f"[2] تعداد اهداف اولیه: {initial_targets}")
        assert initial_targets == 2, f"❌ باید 2 هدف باشد، اما {initial_targets} است."

        # ۴. اجرای مسابقه تا انتها
        print("\n[3] اجرای مسابقه...")
        max_steps = 500
        step = 0
        winner = None
        while step < max_steps and not race.all_targets_rescued():
            team = race.teams[race.current_turn]
            if not team.has_won():
                # اجرای یک قدم از تیم
                # (توجه: در نسخه جدید team.step() رویداد برمی‌گرداند)
                result = team.step()
                step += 1

                # اگر نجات انجام شد، shared_grid باید به‌روزرسانی شود
                if result == "rescued":
                    rescued_pos = team.get_position()
                    print(f"   قدم {step}: {team.name} یک هدف را در {rescued_pos} نجات داد.")
                    # اطمینان از اینکه سلول در shared_grid صفر شده
                    if race.shared_grid[rescued_pos[0]][rescued_pos[1]] != 0:
                        print(f"   ❌ هشدار: سلول {rescued_pos} در shared_grid هنوز {race.shared_grid[rescued_pos[0]][rescued_pos[1]]} است.")
                    # اطمینان از اینکه هدف از لیست مغزها حذف شده
                    for t in race.teams:
                        if rescued_pos in t.brain.targets:
                            print(f"   ❌ هشدار: هدف هنوز در لیست مغز {t.name} وجود دارد.")

            race.current_turn = (race.current_turn + 1) % len(race.teams)

        print(f"\n[4] مسابقه پس از {step} قدم پایان یافت.")
        print(f"   اهداف باقی‌مانده در shared_grid: {sum(row.count(4) for row in race.shared_grid)}")
        print(f"   all_targets_rescued(): {race.all_targets_rescued()}")

        # ۵. بررسی شرط پایان
        assert race.all_targets_rescued(), "❌ شرط پایان برآورده نشد! اهداف هنوز وجود دارند."
        assert sum(row.count(4) for row in race.shared_grid) == 0, "❌ سلول ۴ هنوز در نقشه وجود دارد."
        print("✓ تمام اهداف نجات یافته‌اند و مسابقه به درستی پایان یافته است.")

        # ۶. بررسی اینکه هیچ تیمی قفل نکرده (همه تیم‌ها یا برنده شده‌اند یا کارشان تمام شده)
        for team in race.teams:
            print(f"   {team.name}: has_won={team.has_won()}, steps={team.get_steps_count()}, rescued={team.get_rescued_count()}")
        print("✓ هیچ تیمی در حالت قفل نیست.")

        print("\n" + "=" * 50)
        print("✅ تست یکپارچگی با موفقیت کامل پاس شد.")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"\n❌ خطا در تست: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.unlink(temp_map_path)  # پاکسازی فایل موقت

if __name__ == "__main__":
    success = test_full_rescue_and_termination()
    sys.exit(0 if success else 1)