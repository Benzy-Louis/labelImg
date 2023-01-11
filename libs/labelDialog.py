try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from libs.utils import new_icon, label_validator, trimmed

BB = QDialogButtonBox


class LabelDialog(QDialog):

    def __init__(self, text="Enter object label", parent=None, list_item=None, predef_classes_file=None):
        super(LabelDialog, self).__init__(parent)

        self.list_item = list_item
        self.edit = QLineEdit()
        self.edit.setText(text)
        self.edit.setValidator(label_validator())
        self.edit.editingFinished.connect(self.post_process)
        self.predef_classes_file = predef_classes_file

        model = QStringListModel()
        model.setStringList(self.list_item)
        completer = QCompleter()
        completer.setModel(model)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.edit.setCompleter(completer)

        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        self.button_box = bb = BB(BB.Ok | BB.Cancel, Qt.Horizontal, self)
        bb.button(BB.Ok).setIcon(new_icon('done'))
        bb.button(BB.Cancel).setIcon(new_icon('undo'))
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)

        if self.list_item is not None and len(self.list_item) > 0:
            self.list_widget = QListWidget(self)
            for item in self.list_item:
                self.list_widget.addItem(item)
            self.list_widget.itemClicked.connect(self.list_item_click)
            self.list_widget.itemDoubleClicked.connect(
                self.list_item_double_click)
            layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def save_new_label(self, label):
        import os
        with open(self.predef_classes_file, 'a', encoding='utf-8') as f:
            # Check if the file is empty
            if os.path.getsize(self.predef_classes_file) == 0:
                # If the file is empty, don't add a newline character before the label
                f.write(label)
            else:
                # If the file is not empty, add a newline character before the label
                f.write('\n' + label)

    def validate(self):
        label = trimmed(self.edit.text())
        if label not in self.list_item:
            self.save_new_label(label)
        if label:
            self.accept()

    def post_process(self):
        self.edit.setText(trimmed(self.edit.text()))

    def pop_up(self, text='', move=True):
        """
        Shows the dialog, setting the current text to `text`, and blocks the lcaller until the user has made a choice.
        If the user entered a label, that label is returned, otherwise (i.e. if the user cancelled the action)
        `None` is returned.
        """
        self.parent().load_predefined_classes(
            self.predef_classes_file)  # Reload the predefined classes
        if self.list_item is not None and len(self.list_item) > 0:
            self.list_widget.clear()  # Clear the list widget
        for item in self.parent().label_hist:  # Populate the list widget with the updated predefined classes
            self.list_widget.addItem(item)
        self.edit.setText(text)
        self.edit.setSelection(0, len(text))
        self.edit.setFocus(Qt.PopupFocusReason)
        if move:
            cursor_pos = QCursor.pos()
            parent_bottom_right = self.parentWidget().geometry()
            max_x = parent_bottom_right.x() + parent_bottom_right.width() - \
                self.sizeHint().width()
            max_y = parent_bottom_right.y() + parent_bottom_right.height() - \
                self.sizeHint().height()
            max_global = self.parentWidget().mapToGlobal(QPoint(max_x, max_y))
            if cursor_pos.x() > max_global.x():
                cursor_pos.setX(max_global.x())
            if cursor_pos.y() > max_global.y():
                cursor_pos.setY(max_global.y())
            self.move(cursor_pos)
        return trimmed(self.edit.text()) if self.exec_() else None

    def list_item_click(self, t_qlist_widget_item):
        text = trimmed(t_qlist_widget_item.text())
        self.edit.setText(text)

    def list_item_double_click(self, t_qlist_widget_item):
        self.list_item_click(t_qlist_widget_item)
        self.validate()
