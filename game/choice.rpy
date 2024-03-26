## 选择屏幕 ########################################################################
##
## 此屏幕用于显示由 menu 语句生成的游戏内选项。参数 items 是一个对象列表，每个对
## 象都有字幕和动作字段。
##
## https://www.renpy.cn/doc/screen_special.html#choice

init python:
    # 第一次碰到menu时新建记录，如果有选项是引用另一个menu也需要标记，如果已存在则直接返回
    def new_choice_record(mark, items):
        if items[0][0] == "Menu Prediction":
            return
        # 初始化选项记录表
        if mark not in _chosen:
            _chosen[mark] = record = {}
        return _chosen[mark]

    def set_choice_record(record, item, state=True):
        print("set recort", record, item)
        record[item] = state
        print("seted recort", record, item)


    # 判断一个选项是否被选过
    def judge_item_chosen(state):
        # 如果当前选项不需要记录，那就返回True
        if state == None:
            return True
        # 如果是bool值的话则直接返回
        if isinstance(state, bool):
            return state
        # 否则是字符串，说明引用了另一个menu
        # 如果这个menu连记录都没有，说明没有碰到过，那肯定没选过
        if state not in _chosen_id:
            print("【%s】没有记录！" % str(state))
            return False
        # 有记录，则遍历这个子menu的每个记录
        else:
            child_menu = _chosen_id[state]
            # 只要有一个没选过那就是没选过
            for i in child_menu.values():
                if judge_item_chosen(i) == False:
                    return False
            # 都选过那就选过了
            return True

# 默认计时选项的时间
default choice_time = 15.0

# 记录选项是否被选过的字典
default _chosen = {}
# 通过id索引
default _chosen_id = {}

# items:
# t:限时选项的时间，True 使用默认时间，False 就是不限时选项
# id:标记当前 menu ，可以通过_chosen_id找到选项记录
# r:是否对当前 menu 进行记录，如果不记录的话就不显示是否游览过了
screen choice(items, t=False, id=None, r=True):
    style_prefix "choice"

    # 如果是限时选项
    if t:
        # 没有指定时间就使用默认时间
        if t is True:
            $ t = choice_time
        # 时间条
        fixed:
            bar:
                value AnimatedValue(0, 100, t, 100)
                xysize (669,47)
                left_bar "gui/time/timebar_hover.png"
                right_bar "gui/time/timebar_idle.png"
                align (0.535, 0.925)
            add "gui/time/decorate.png"
        # 返回计时器
        timer t:
            action Return(0)

    # 需要记录
    if r:
        python:
            # 通过获取上下文获得选项的唯一标记
            choice_mark = renpy.game.context().current
            # 用这个标记去获得选项记录
            record = new_choice_record(choice_mark, items)
            # 如果该menu有id，还需要建立id索引
            if id != None:
                _chosen_id[id] = record
        vbox:
            for index, i in enumerate(items):
                $ item = i[0]
                # 当前选项是否被隐藏
                $ hide = i.kwargs.get("h")
                if hide == True:
                    $ record[item] = True
                # 不记录这个选项，永远为 None
                elif i.kwargs.get("r") == False:
                    $ record[item] = None
                    textbutton i.caption action i.action
                # 记录这个选项
                else:
                    # 是否有子 menu
                    $ no_child = "child" not in i.kwargs
                    # 是否有 id
                    $ id = i.kwargs.get("id")
                    if id != None:
                        $ item = id
                    # 没有子 menu
                    if no_child:
                        # 之前没记录过，是新出现的选项
                        if item not in record:
                            $ is_chosen = record[item] = False
                        else:
                            $ is_chosen = record[item]
                    # 有子 menu
                    else:
                        $ record[item] = i.kwargs["child"]
                        $ is_chosen = judge_item_chosen(record[item])
                    textbutton i.caption:
                        # 已经选过了
                        if is_chosen:
                            foreground "gui/button/choice_tik.png"
                            #background "gui/button/choice_read_background.png"
                        if no_child:
                            action [Function(set_choice_record, record, item), i.action]
                        else:
                            action i.action

    # 不需要记录
    else:
        vbox:
            for i in items:
                textbutton i.caption:
                    action i.action
                    # 有标题则选项稍向下
                    if title:
                        yoffset 60

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