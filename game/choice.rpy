## 选择屏幕 ########################################################################
##
## 此屏幕用于显示由 menu 语句生成的游戏内选项。参数 items 是一个对象列表，每个对
## 象都有字幕和动作字段。
##
## https://www.renpy.cn/doc/screen_special.html#choice

init python:
    # 获取当前上下文中菜单对应的选项记录
    def get_choice_record(items):
        # Prediction 时跳过
        if items[0][0] == "Menu Prediction":
            return
        mark = renpy.game.context().current
        # 第一次遇到该菜单，新建记录
        if mark not in _chosen:
            _chosen[mark] = record = {}
        return _chosen[mark]

    def set_choice_record(record, item, state=True):
        record[item] = state

    # 判断一个选项是否被选过
    # None: 当前选项不需要记录，判断为选过
    # bool：返回 bool 值本身，作为递归的终点
    # 字符串：该选项引用了另一个菜单，通过这个菜单的所有选项是否选过判断当前选项是否选过
    def judge_item_chosen(state):
        if state == None:
            return True
        if isinstance(state, bool):
            return state
        # 没有记录的菜单，没有选过
        if state not in _chosen_id:
            print("【%s】没有记录！" % str(state))
            return False
        # 有记录的菜单，所有选项都选过则判断为选过，否则没选过
        else:
            child_menu = _chosen_id[state]
            # 只要有一个没选过那就是没选过
            for i in child_menu.values():
                if judge_item_chosen(i) == False:
                    return False
            return True

# 默认计时选项的时间
default choice_time = 15.0

# 记录选项是否被选过的字典，key 是 context 字符串
default _chosen = {}
# 通过 id 索引，key 是菜单的 id 字符串
default _chosen_id = {}

# items:
# t: Number 限时选项的时间，True 使用默认时间，False 就是不限时选项
# id: 标记当前 menu ，可以通过_chosen_id找到选项记录
# r: 是否对当前 menu 选过标记
screen choice(items, t=False, id=None, r=True):
    style_prefix "choice"

    # 限时选项
    if t:
        # 没有指定时间就使用默认时间
        if t is True:
            $ t = choice_time
        # 时间条
        fixed:
            bar:
                value AnimatedValue(0, 100, t, 100)
                xysize (669,47)
                left_bar "gui/choice/timebar_hover.png"
                right_bar "gui/choice/timebar_idle.png"
                align (0.535, 0.925)
            add "gui/choice/decorate.png"
        # 返回计时器
        timer t:
            action Return(0)

    # 选过标记
    if r:
        python:
            # 获取当前选项的记录
            record = get_choice_record(items)
            # 如果该menu有id，还需要建立id索引
            if id != None:
                _chosen_id[id] = record
        vbox:
            for index, i in enumerate(items):
                $ item = i[0] + "-" + str(index)
                # 不记录这个选项，标记为 None
                if i.kwargs.get("r") == False:
                    $ record[item] = None
                    textbutton i.caption action i.action
                # 记录这个选项
                else:
                    $ child_id = i.kwargs.get("child")
                    # 没有子菜单，根据历史记录决定是否选过
                    if not child_id:
                        # 之前没记录过，是新出现的选项
                        if item not in record:
                            $ is_chosen = record[item] = False
                        else:
                            $ is_chosen = record[item]
                    # 有子菜单，根据子菜单是否全都选过决定是否选过
                    else:
                        $ record[item] = child_id
                        $ is_chosen = judge_item_chosen(child_id)
                    textbutton i.caption:
                        # 选过则显示选过标记
                        if is_chosen:
                            foreground "gui/choice/choice_tik.png"
                        # 不包含子菜单的选项，选择后直接标记选过
                        if not child_id:
                            action [Function(set_choice_record, record, item), i.action]
                        else:
                            action i.action
    # 不需要记录
    else:
        vbox:
            for i in items:
                textbutton i.caption:
                    action i.action

style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ypos 270
    yanchor 0.5

    spacing gui.choice_spacing

style choice_button is default:
    properties gui.button_properties("choice_button")

style choice_button_text is default:
    properties gui.button_text_properties("choice_button")