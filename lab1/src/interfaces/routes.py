from flask import Blueprint, render_template, redirect, url_for, flash, request
from src.core.kindergarten import Kindergarten
from src.utils.exceptions import (
    KindergartenException, ChildNotFoundError, InvalidAgeError,
    GameNotFoundError, MaterialNotFoundError, InvalidStateError,
    GameAgeError, GroupError
)

main_bp = Blueprint('main', __name__)

kindergarten = Kindergarten("Анна Петровна")


@main_bp.route('/')
def index():
    """Главная страница"""
    children = kindergarten.get_all_children()
    groups = kindergarten.get_all_groups()
    materials = kindergarten.get_all_materials()
    games = kindergarten.get_all_games()
    
    return render_template(
        'index.html',
        title='Детский сад №75',
        teacher=kindergarten.teacher,
        children=children,
        groups=groups,
        materials=materials,
        games=games
    )


# ========== УПРАВЛЕНИЕ ДЕТЬМИ ==========

@main_bp.route('/child/add', methods=['GET', 'POST'])
def add_child():
    """Добавить ребенка"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        try:
            age = int(request.form.get('age', 0))
        except ValueError:
            flash("Возраст должен быть числом", "error")
            return redirect(url_for('main.add_child'))
        
        if not name:
            flash("Имя не может быть пустым", "error")
            return redirect(url_for('main.add_child'))
        
        try:
            child = kindergarten.add_child(name, age)
            flash(f"Ребенок {child.name} добавлен!", "success")
            
            # Определяем в группу, если выбрана
            group_name = request.form.get('group_name')
            if group_name:
                try:
                    result = kindergarten.assign_child_to_group(child.name, group_name)
                    flash(result, "success")
                except GroupError as e:
                    flash(str(e), "error")
            
            return redirect(url_for('main.index'))
        except InvalidAgeError as e:
            flash(str(e), "error")
            return redirect(url_for('main.add_child'))
    
    groups = kindergarten.get_all_groups()
    return render_template('add_child.html', title='Добавить ребенка', groups=groups)


@main_bp.route('/child/<name>/feed')
def feed_child(name):
    try:
        result = kindergarten.feed_child(name)
        flash(result["message"], "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for('main.index'))


@main_bp.route('/child/<name>/sleep')
def put_to_sleep(name):
    try:
        result = kindergarten.put_to_sleep(name)
        flash(result["message"], "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for('main.index'))


@main_bp.route('/child/<name>/wake')
def wake_up(name):
    try:
        result = kindergarten.wake_up(name)
        flash(result["message"], "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for('main.index'))


@main_bp.route('/child/<name>/finish_game')
def finish_game(name):
    try:
        result = kindergarten.finish_game(name)
        flash(result["message"], "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for('main.index'))


@main_bp.route('/child/<name>/dropoff')
def drop_off(name):
    try:
        result = kindergarten.drop_off_child(name)
        flash(result["message"], "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for('main.index'))


@main_bp.route('/child/<name>/pickup')
def pickup(name):
    try:
        result = kindergarten.pickup_child(name)
        flash(result["message"], "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for('main.index'))


# ========== ИГРЫ ==========

@main_bp.route('/game/play', methods=['GET', 'POST'])
def play_game():
    """Поиграть в игру"""
    if request.method == 'POST':
        child_name = request.form.get('child_name', '').strip()
        game_name = request.form.get('game_name', '').strip()
        
        try:
            result = kindergarten.start_game(child_name, game_name)
            flash(result["message"], "success")
        except (ChildNotFoundError, GameNotFoundError, GameAgeError, InvalidStateError) as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Ошибка: {e}", "error")
        
        return redirect(url_for('main.index'))
    
    children = [c for c in kindergarten.get_all_children() if c.state != 'left']
    games = [g for g in kindergarten.get_all_games() if not g.is_educational]
    
    return render_template('play_game.html', title='Поиграть', children=children, games=games)


# ========== МАТЕРИАЛЫ ==========

@main_bp.route('/materials/add', methods=['GET', 'POST'])
def add_material():
    """Добавить учебный материал"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        try:
            quantity = int(request.form.get('quantity', 0))
        except ValueError:
            flash("Количество должно быть числом", "error")
            return redirect(url_for('main.add_material'))
        
        if not title:
            flash("Название не может быть пустым", "error")
            return redirect(url_for('main.add_material'))
        
        try:
            kindergarten.add_material(title, quantity)
            flash(f"Материал '{title}' добавлен!", "success")
        except Exception as e:
            flash(str(e), "error")
        
        return redirect(url_for('main.index'))
    
    return render_template('add_material.html', title='Добавить материал')


@main_bp.route('/games/add', methods=['GET', 'POST'])
def add_game():
    """Добавить игру или учебное занятие"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_educational = request.form.get('is_educational') == 'on'
        
        try:
            min_age = int(request.form.get('min_age', 0))
            max_age = int(request.form.get('max_age', 0))
        except ValueError:
            flash("Возраст должен быть числом", "error")
            return redirect(url_for('main.add_game'))
        
        required_materials_raw = request.form.get('required_materials', '').strip()
        required_materials = [m.strip() for m in required_materials_raw.split(',') if m.strip()]
        
        if not name:
            flash("Название не может быть пустым", "error")
            return redirect(url_for('main.add_game'))
        
        try:
            kindergarten.add_game(name, description, min_age, max_age, required_materials, is_educational)
            game_type = "учебное занятие" if is_educational else "игра"
            flash(f"{game_type.capitalize()} '{name}' добавлена!", "success")
        except Exception as e:
            flash(str(e), "error")
        
        return redirect(url_for('main.index'))
    
    return render_template('add_game.html', title='Добавить игру/занятие')


# ========== ГРУППЫ ==========

@main_bp.route('/groups')
def show_groups():
    """Показать все группы"""
    groups = kindergarten.get_all_groups()
    return render_template('groups.html', title='Группы', groups=groups)


@main_bp.route('/group/assign', methods=['GET', 'POST'])
def assign_to_group():
    """Определить ребенка в группу"""
    if request.method == 'POST':
        child_name = request.form.get('child_name', '').strip()
        group_name = request.form.get('group_name', '').strip()
        
        try:
            result = kindergarten.assign_child_to_group(child_name, group_name)
            flash(result, "success")
        except (ChildNotFoundError, GroupError) as e:
            flash(str(e), "error")
        
        return redirect(url_for('main.index'))
    
    children = kindergarten.get_all_children()
    groups = kindergarten.get_all_groups()
    return render_template('assign_group.html', title='Определить в группу', children=children, groups=groups)


# ========== УЧЕБНЫЙ ПРОЦЕСС ==========

@main_bp.route('/educational/process', methods=['GET', 'POST'])
def educational_process():
    """Организовать учебный процесс"""
    if request.method == 'POST':
        game_name = request.form.get('game_name', '').strip()
        group_name = request.form.get('group_name', '') or None
        
        try:
            result = kindergarten.organize_educational_process(game_name, group_name)
            flash(result, "success")
        except GameNotFoundError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Ошибка: {e}", "error")
        
        return redirect(url_for('main.index'))
    
    educational_games = [g for g in kindergarten.get_all_games() if g.is_educational]
    groups = kindergarten.get_all_groups()
    
    return render_template(
        'educational_process.html',
        title='Учебный процесс',
        games=educational_games,
        groups=groups
    )


@main_bp.route('/educational/report')
def educational_report():
    """Отчет об учебном процессе"""
    report = kindergarten.get_educational_report()
    return render_template('report.html', title='Отчет', report=report)


# ========== РОДИТЕЛИ ==========

@main_bp.route('/parent/add', methods=['GET', 'POST'])
def add_parent():
    """Добавить родителя ребенку"""
    if request.method == 'POST':
        parent_name = request.form.get('parent_name', '').strip()
        child_name = request.form.get('child_name', '').strip()
        
        if not parent_name or not child_name:
            flash("Заполните все поля", "error")
            return redirect(url_for('main.add_parent'))
        
        try:
            child = kindergarten.get_child_or_raise(child_name)
            kindergarten.add_parent(parent_name, child)
            flash(f"Родитель {parent_name} добавлен для {child_name}", "success")
        except Exception as e:
            flash(str(e), "error")
        
        return redirect(url_for('main.index'))
    
    children = kindergarten.get_all_children()
    return render_template('add_parent.html', title='Добавить родителя', children=children)


# ========== СОХРАНЕНИЕ ==========

@main_bp.route('/save')
def save_state():
    """Сохранить состояние"""
    try:
        kindergarten.save_state()
        flash("Состояние сохранено!", "success")
    except Exception as e:
        flash(f"Ошибка сохранения: {e}", "error")
    return redirect(url_for('main.index'))

@main_bp.route('/child/<name>/play')
def play_for_child(name):
    """Страница выбора игры для конкретного ребенка"""
    child = kindergarten.get_child_or_raise(name)
    games = [g for g in kindergarten.get_all_games() if not g.is_educational and g.can_play(child.age)]
    
    if not games:
        flash(f"Для {child.name} нет подходящих игр", "error")
        return redirect(url_for('main.index'))
    
    return render_template('play_for_child.html', child=child, games=games)


@main_bp.route('/child/<name>/educational')
def educational_for_child(name):
    """Страница выбора занятия для конкретного ребенка"""
    child = kindergarten.get_child_or_raise(name)
    lessons = [g for g in kindergarten.get_all_games() if g.is_educational and g.can_play(child.age)]
    
    if not lessons:
        flash(f"Для {child.name} нет подходящих занятий", "error")
        return redirect(url_for('main.index'))
    
    return render_template('educational_for_child.html', child=child, lessons=lessons)


@main_bp.route('/child/<name>/start_game/<game_name>')
def start_game_for_child(name, game_name):
    """Запустить игру для конкретного ребенка"""
    try:
        result = kindergarten.start_game(name, game_name)
        flash(result["message"], "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for('main.index'))


@main_bp.route('/child/<name>/start_lesson/<lesson_name>')
def start_lesson_for_child(name, lesson_name):
    """Запустить занятие для конкретного ребенка"""
    try:
        child = kindergarten.get_child_or_raise(name)
        lesson = kindergarten.get_game_or_raise(lesson_name)
        
        if not lesson.is_educational:
            flash(f"'{lesson_name}' не является учебным занятием", "error")
            return redirect(url_for('main.index'))
        
        if child.state != 'awake':
            flash(f"{name} не может начать занятие (сейчас {child.state})", "error")
            return redirect(url_for('main.index'))
        
        # Проверка материалов
        materials_dict = {m.title: m for m in kindergarten.materials}
        missing = lesson.check_materials(materials_dict)
        
        if missing:
            flash(f"Не хватает материалов: {', '.join(missing)}", "error")
            return redirect(url_for('main.index'))
        
        # Используем материалы
        for material_name in lesson.required_materials:
            if material_name in materials_dict:
                materials_dict[material_name].use(1)
        
        # Начинаем занятие
        child.update_state("playing")
        child._in_lesson = True
        
        flash(f"Проведено занятие '{lesson.name}' с {child.name}", "success")
    except Exception as e:
        flash(str(e), "error")
    
    return redirect(url_for('main.index'))