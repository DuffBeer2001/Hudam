#외부IP로 MYSQL 접속하여 조회하는 프로그램
#최초생성일자 20251208
#최종수정일자 20251208

#개선할점
#SSH을 이용하여 보안 강화
#ONLY READ to READ AND WRITE 가능하게



import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton, QLineEdit, QDialog, QMessageBox, QDateEdit, QFormLayout
)
from PyQt5.QtCore import Qt, QDate, QEvent
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtGui import QFont, QFontDatabase
import pymysql
import PyQt5

# ===================== DB 함수 =====================

DB_CONFIG = {
    'host': #'IP 주소 입력',
    'port': #보통 3306,
    'user': #'user',
    'password': #'',
    'db': #'',
    'charset': 'utf8'
}

def get_db_connection():
    try:
        return pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            db=DB_CONFIG['db'],
            charset=DB_CONFIG['charset']
        )
    except Exception as e:
        raise e

#전화번호 뒤4자리로 조회하기
def search_by_phone_last4(last4):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = """
                SELECT * FROM person
                WHERE RIGHT(REPLACE(REPLACE(REPLACE(phone_number, '-', ''), '.', ''), ' ', ''), 4) = %s
            """
            cur.execute(sql, (last4,))
            return cur.fetchall()
    except Exception as e:
        print("DB 오류:", e)
        return []
    finally:
        try:
            conn.close()
        except:
            pass

#이름으로 조회하기
def search_by_name(name):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = "SELECT * FROM person WHERE person_name = %s"
            cur.execute(sql, (name,))
            return cur.fetchall()
    except Exception as e:
        print("DB 오류:", e)
        return []
    finally:
        try:
            conn.close()
        except:
            pass

def get_counsel_by_person_id(person_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = "SELECT * FROM counsel WHERE person_id = %s"
            cur.execute(sql, (person_id,))
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return results, columns
    except Exception as e:
        print("DB 오류:", e)
        return [], []
    finally:
        try:
            conn.close()
        except:
            pass

def get_status_table_with_phone_by_date(date_str):
    sql = '''
    SELECT
      c.counsel_date,
      c.title AS 상담방식,
      p.person_name AS 고객명,
      p.phone_number AS 전화번호,
      o.cnt AS 탕약차수,
      d.drug_name AS 탕약세기,
      d.drug_dose AS 용량
    FROM counsel c
    LEFT JOIN person p ON c.person_id = p.person_id
    LEFT JOIN orders o ON c.person_id = o.person_id
    LEFT JOIN drug d ON o.drug_id = d.drug_id
    WHERE c.counsel_date = %s
    ORDER BY p.person_name, o.cnt DESC
    '''
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (date_str,))
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return results, columns
    except Exception as e:
        print("DB 오류:", e)
        return [], []
    finally:
        try:
            conn.close()
        except:
            pass

def get_delivery_table_by_period(start_date, end_date):
    sql = '''
    SELECT
      od.order_date AS 주문날짜,
      od.send_date AS 보낸날짜,
      od.receive_date AS 수령날짜,
      p.person_name AS 고객명,
      p.phone_number AS 전화번호,
      d.drug_name AS 탕약세기,
      d.drug_dose AS 탕약용량,
      o.dose AS 탕약일수,
      o.eat_way AS 참고사항,
      o.delivery_type AS 배송방법,
      od.place_name AS 배송지명,
      od.recipient AS 수령인,
      od.recipient_phone1 AS 수령인연락처1,
      od.recipient_phone2 AS 수령인연락처2,
      od.address AS 배송지,
      od.order_id AS 주문ID,
      od.person_id AS 고객ID
    FROM orders_delivery od
    LEFT JOIN person p ON od.person_id = p.person_id
    LEFT JOIN orders o ON od.order_id = o.order_id
    LEFT JOIN drug d ON o.drug_id = d.drug_id
    WHERE od.order_date BETWEEN %s AND %s
    ORDER BY od.order_date ASC
    '''
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(sql, (start_date, end_date))
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return results, columns
    except Exception as e:
        print("DB 오류:", e)
        return [], []
    finally:
        try:
            conn.close()
        except:
            pass

def get_person_info(person_id):
    # person_name, sex, age, height, weight, target_weight
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = """
            SELECT person_name, sex, age, height, weight, target_weight
            FROM person
            WHERE person_id = %s
            """
            cur.execute(sql, (person_id,))
            result = cur.fetchone()
            return result
    except Exception as e:
        print("DB 오류:", e)
        return None
    finally:
        try:
            conn.close()
        except:
            pass

def get_person_address(person_id):
    # place_name, address, address_detail
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = """
            SELECT place_name, address, address_detail
            FROM address
            WHERE person_id = %s
            LIMIT 1
            """
            cur.execute(sql, (person_id,))
            result = cur.fetchone()
            return result
    except Exception as e:
        print("DB 오류:", e)
        return None
    finally:
        try:
            conn.close()
        except:
            pass

def get_old_chart(person_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = "SELECT chart_text FROM old_chart WHERE person_id = %s"
            cur.execute(sql, (person_id,))
            result = cur.fetchall()
            return [r[0] for r in result]  # chart_text만 리스트로 반환
    except Exception as e:
        print("old_chart 조회 오류:", e)
        return []
    finally:
        try:
            conn.close()
        except:
            pass

def get_old_note(person_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = "SELECT memo FROM old_note WHERE person_id = %s"
            cur.execute(sql, (person_id,))
            result = cur.fetchall()
            return [r[0] for r in result]
    except Exception as e:
        print("old_note 조회 오류:", e)
        return []
    finally:
        try:
            conn.close()
        except:
            pass

# ===================== DB 연결 설정 다이얼로그 =====================

class DbConfigDialog(QDialog):
    def __init__(self, default_host, default_port, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DB 서버 연결 정보 입력")
        self.setModal(True)
        self.resize(350, 140)
        layout = QFormLayout()
        self.host_edit = QLineEdit(default_host)
        self.port_edit = QLineEdit(str(default_port))
        self.port_edit.setValidator(QtGui.QIntValidator(1, 65535))
        layout.addRow("Host:", self.host_edit)
        layout.addRow("Port:", self.port_edit)
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("확인")
        self.cancel_btn = QPushButton("취소")
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(btn_layout)
        self.setLayout(layout)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_values(self):
        return self.host_edit.text().strip(), int(self.port_edit.text().strip())

# ===================== 위젯 클래스 =====================

class CounselDialog(QDialog):
    def __init__(self, person_id, ns_font_name):
        super().__init__()
        self.setWindowTitle(f"고객 상세 정보")
        self.showMaximized()
        main_layout = QHBoxLayout()

        # ==== (왼쪽) 상담 테이블 or 대체 표시 ====
        left_layout = QVBoxLayout()
        results, columns = get_counsel_by_person_id(person_id)
        wanted_indexes = [2, 4, 6, 7, 8, 9]
        wanted_columns = ["상담날짜", "상담방식", "탕약현황", "상담내용1", "상담내용2", "상담내용3"]

        if results:
            table = QTableWidget(len(results), len(wanted_indexes))
            table.setFont(QFont(ns_font_name, 12))
            table.setHorizontalHeaderLabels(wanted_columns)
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            for row_idx, row in enumerate(results):
                for col_idx, wanted in enumerate(wanted_indexes):
                    value = str(row[wanted]) if row[wanted] is not None else ""
                    item = QTableWidgetItem(value)
                    item.setFont(QFont(ns_font_name, 12))
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    table.setItem(row_idx, col_idx, item)
            table.resizeRowsToContents()
            table.setColumnWidth(5, 400)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            # ② 선택 배경색 지정
            table.setStyleSheet("""
              QTableWidget::item:selected {
                background-color: #FFD700;    /* Gold */
                color: black;}""")
            # 헤더 색상 스타일 적용
            table.horizontalHeader().setStyleSheet(
                "QHeaderView::section {"
                "background-color: 		#333333;"
                "color: white;"
                "font-weight: bold;"
                "font-size: 20px;"
                "}"
            )

            table.verticalHeader().setStyleSheet(
                "QHeaderView::section {"
                "background-color: 	#333333;"
                "color: white;"
                "font-weight: bold;"
                "font-size: 20px;"
                "qproperty-alignment: AlignCenter;"
                "}"
            )
            left_layout.addWidget(table)

            # 상담정보 없을 때 old_chart, old_note 확인
            old_chart_texts = get_old_chart(person_id)
            old_notes = get_old_note(person_id)

            show_any = False
            # 1. old_chart (표)
            if old_chart_texts:
                show_any = True
                label = QLabel("이전 차트 정보")
                label.setFont(QFont(ns_font_name, 14))
                label.setStyleSheet("font-weight: bold; color: navy;")
                left_layout.addWidget(label)

                table = QTableWidget(len(old_chart_texts), 1)
                table.setFont(QFont(ns_font_name, 12))
                table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                table.setHorizontalHeaderLabels(["차트 내용"])
                for row_idx, chart in enumerate(old_chart_texts):
                    item = QTableWidgetItem(chart)
                    item.setFont(QFont(ns_font_name, 12))
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                    table.setItem(row_idx, 0, item)
                table.resizeRowsToContents()
                table.setColumnWidth(0, 1000)
                table.setStyleSheet("""
                    QTableWidget::item:selected {
                        background-color: #FFD700;    /* Gold */
                        color: black;}""")
                left_layout.addWidget(table)

            # 2. old_note (표)
            if old_notes:
                show_any = True
                label = QLabel("이전 메모 정보")
                label.setFont(QFont(ns_font_name, 14))
                label.setStyleSheet("font-weight: bold; color: darkred;")
                left_layout.addWidget(label)

                table = QTableWidget(len(old_notes), 1)
                table.setFont(QFont(ns_font_name, 12))
                table.setHorizontalHeaderLabels(["메모 내용"])
                for row_idx, memo in enumerate(old_notes):
                    item = QTableWidgetItem(memo)
                    item.setFont(QFont(ns_font_name, 12))
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                    table.setItem(row_idx, 0, item)
                table.resizeRowsToContents()
                table.setColumnWidth(0, 1000)
                table.setStyleSheet("""
                   QTableWidget::item:selected {
                    background-color: #FFD700;    /* Gold */
                    color: black;}""")
                table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                left_layout.addWidget(table)

            if not show_any:
                label = QLabel("해당 고객 상담 정보가 없습니다")
                label.setFont(QFont(ns_font_name, 14))
                label.setStyleSheet("color: red;")
                left_layout.addWidget(label)
        else:
            # 상담정보 없을 때 old_chart, old_note 확인
            old_chart_texts = get_old_chart(person_id)
            old_notes = get_old_note(person_id)

            show_any = False
            # 1. old_chart (표)
            if old_chart_texts:
                show_any = True
                label = QLabel("이전 차트 정보")
                label.setFont(QFont(ns_font_name, 14))
                label.setStyleSheet("font-weight: bold; color: navy;")
                left_layout.addWidget(label)

                table = QTableWidget(len(old_chart_texts), 1)
                table.setFont(QFont(ns_font_name, 12))
                table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                table.setHorizontalHeaderLabels(["차트 내용"])
                for row_idx, chart in enumerate(old_chart_texts):
                    item = QTableWidgetItem(chart)
                    item.setFont(QFont(ns_font_name, 12))
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                    table.setItem(row_idx, 0, item)
                table.resizeRowsToContents()
                table.setColumnWidth(0, 1000)
                table.setStyleSheet("""
                    QTableWidget::item:selected {
                        background-color: #FFD700;    /* Gold */
                        color: black;}""")
                left_layout.addWidget(table)

            # 2. old_note (표)
            if old_notes:
                show_any = True
                label = QLabel("이전 메모 정보")
                label.setFont(QFont(ns_font_name, 14))
                label.setStyleSheet("font-weight: bold; color: darkred;")
                left_layout.addWidget(label)

                table = QTableWidget(len(old_notes), 1)
                table.setFont(QFont(ns_font_name, 12))
                table.setHorizontalHeaderLabels(["메모 내용"])
                for row_idx, memo in enumerate(old_notes):
                    item = QTableWidgetItem(memo)
                    item.setFont(QFont(ns_font_name, 12))
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                    table.setItem(row_idx, 0, item)
                table.resizeRowsToContents()
                table.setColumnWidth(0, 1000)
                table.setStyleSheet("""
                    QTableWidget::item:selected {
                        background-color: #FFD700;    /* Gold */
                        color: black;}""")
                table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                left_layout.addWidget(table)

            if not show_any:
                label = QLabel("해당 고객 상담 정보가 없습니다")
                label.setFont(QFont(ns_font_name, 14))
                label.setStyleSheet("color: red;")
                left_layout.addWidget(label)

        main_layout.addLayout(left_layout, 2)

        # ==== (오른쪽) 인적/주소 패널 ====
        right_layout = QFormLayout()
        # 1. person 정보
        person_info = get_person_info(person_id)
        person_labels = ["이름", "성별", "나이", "키", "몸무게", "목표체중"]
        if person_info:
            for label_text, value in zip(person_labels, person_info):
                val = str(value) if value is not None else ""
                lbl = QLabel(val)
                lbl.setFont(QFont(ns_font_name, 12))
                right_layout.addRow(f"{label_text}:", lbl)
        else:
            right_layout.addRow("고객정보", QLabel("정보 없음"))

        # 2. address 정보
        address_info = get_person_address(person_id)
        address_labels = ["배송지명", "주소", "상세주소"]
        if address_info:
            for label_text, value in zip(address_labels, address_info):
                val = str(value) if value is not None else ""
                lbl = QLabel(val)
                lbl.setFont(QFont(ns_font_name, 12))
                right_layout.addRow(f"{label_text}:", lbl)
        else:
            right_layout.addRow("주소정보", QLabel("정보 없음"))

        # 위젯으로 감싸서 HBox에 추가
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 1)

        self.setLayout(main_layout)

class CustomerSearchWidget(QWidget):
    def __init__(self, ns_font_name):
        super().__init__()
        self.ns_font_name = ns_font_name
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        search_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("전화번호 뒷자리(4자리) 또는 이름 입력")
        self.input_field.setMaxLength(30)
        self.input_field.setFixedHeight(48)
        self.input_field.setFont(QFont(self.ns_font_name, 16))
        self.input_field.setStyleSheet("font-size: 18px;")

        search_btn = QPushButton("검색")
        search_btn.setFixedHeight(48)
        search_btn.setFont(QFont(self.ns_font_name, 16))
        search_btn.setStyleSheet("font-size: 26px; padding: 6px 30px;")
        search_btn.clicked.connect(self.on_search)
        self.input_field.returnPressed.connect(self.on_search)

        search_layout.addWidget(self.input_field)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        main_layout.addLayout(search_layout)

        self.result_col = ["활성여부","등록일", "이름", "성별", "연령", "연락처", "연락처2 정보", "연락처2", "고객ID"]
        self.wanted_indexes = [20,1, 2, 3, 4, 9, 11, 12, 0]
        self.table = QTableWidget(0, len(self.result_col))
        self.table.setFont(QFont(self.ns_font_name, 12))
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(self.result_col)
        self.table.cellDoubleClicked.connect(self.on_cell_clicked)
        main_layout.addWidget(self.table)

        # ① 행 전체 선택
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # ② 선택 배경색 지정
        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #FFD700;    /* Gold */
                color: black;}
                """)
        # 헤더 색상 스타일 적용
        self.table.horizontalHeader().setStyleSheet(
            "QHeaderView::section {"
            "background-color: 		#333333;"
            "color: white;"
            "font-weight: bold;"
            "font-size: 20px;"
            "}"
        )

        self.table.verticalHeader().setStyleSheet(
            "QHeaderView::section {"
            "background-color: 	#333333;"
            "color: white;"
            "font-weight: bold;"
            "font-size: 20px;"
            "qproperty-alignment: AlignCenter;"
            "}"
        )

        self.no_result_label = QLabel("검색 결과가 없습니다.")
        self.no_result_label.setFont(QFont(self.ns_font_name, 14))
        self.no_result_label.setStyleSheet("color: red; font-weight: bold;")
        self.no_result_label.hide()
        main_layout.addWidget(self.no_result_label)

        self.setLayout(main_layout)

    def on_search(self):
        keyword = self.input_field.text().strip()
        self.no_result_label.hide()
        self.table.setRowCount(0)

        if not keyword:
            QMessageBox.warning(self, "입력 오류", "전화번호 뒷자리 4자리 또는 이름을 입력하세요.")
            return

        if keyword.isdigit() and len(keyword) == 4:
            results = search_by_phone_last4(keyword)
        else:
            results = search_by_name(keyword)

        if not results:
            self.no_result_label.show()
            return

        display_row = 0
        for row in results:
            state = row[20]  # del 필드 인덱스는 20
            if state == 'Y':
                continue  # 삭제된 항목은 표시 안 함
            elif state == 'N':
                state_display = '활성'
            elif state == 'P':
                state_display = '비활성'
            else:
                state_display = '알 수 없음'

            self.table.insertRow(display_row)
            for col_idx, idx in enumerate(self.wanted_indexes):
                if idx == 20:  # del 상태가 표시되는 컬럼이면
                    value = state_display
                else:
                    value = str(row[idx]) if row[idx] is not None else ""
                item = QTableWidgetItem(value)
                item.setFont(QFont(self.ns_font_name, 12))
                self.table.setItem(display_row, col_idx, item)
            display_row += 1

        self.table.setColumnWidth(5, 250)
        self.table.setColumnWidth(7, 250)

    def on_cell_clicked(self, row, col):
        person_id_item = self.table.item(row, 8)
        if person_id_item is not None:
            person_id = person_id_item.text()
            dialog = CounselDialog(person_id, self.ns_font_name)
            dialog.exec_()

class StatusWidget(QWidget):
    def __init__(self, ns_font_name):
        super().__init__()
        self.ns_font_name = ns_font_name
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        date_row = QHBoxLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFont(QFont(self.ns_font_name, 16))
        self.date_edit.setFixedHeight(40)

        self.search_btn = QPushButton("조회")
        self.search_btn.setFont(QFont(self.ns_font_name, 14))
        self.search_btn.setFixedHeight(40)
        self.search_btn.clicked.connect(self.on_search)
        self.date_edit.installEventFilter(self)

        date_row.addWidget(self.date_edit)
        date_row.addWidget(self.search_btn)
        date_row.addStretch()
        layout.addLayout(date_row)

        self.table = QTableWidget()
        self.table.setFont(QFont(self.ns_font_name, 12))
        self.table.verticalHeader().setFixedWidth(50)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # ① 행 전체 선택
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # ② 선택 배경색 지정
        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #FFD700;    /* Gold */
                color: black;
            }
        """)
        # 헤더 색상 스타일 적용
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section,
            QHeaderView::section:checked,
            QHeaderView::section:pressed,
            QHeaderView::section:focus {
                background-color: #333333;
                color: white;
                font-weight: bold;
                font-size: 20px;
            }
        """)

        self.table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
            background-color: 	#333333;
            color: white;
            font-weight: bold;
            font-size: 20px;
            qproperty-alignment: AlignCenter;
            }
        """)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.on_search()

    def eventFilter(self, obj, event):
        if obj == self.date_edit and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.on_search()
                return True
        return super().eventFilter(obj, event)

    def on_search(self):
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        results, columns = get_status_table_with_phone_by_date(date_str)
        show_columns = ['상담날짜', '상담방식', '고객명', '전화번호', '탕약차수', '탕약세기', '용량']

        if results:
            df = pd.DataFrame(results, columns=show_columns)
            # 고객명별 최대 탕약차수만 남김
            max_cnt = df.groupby('고객명')['탕약차수'].max().reset_index()
            filtered_df = pd.merge(df, max_cnt, on=['고객명', '탕약차수'])
            df = filtered_df

            self.table.setColumnCount(len(show_columns))
            self.table.setRowCount(len(df))
            self.table.setHorizontalHeaderLabels(show_columns)
            for row_idx, row in df.iterrows():
                for col_idx, col in enumerate(show_columns):
                    value = row[col]
                    if col == '탕약차수':
                        try:
                            float_val = float(value)
                            if float_val.is_integer():
                                value = str(int(float_val))
                            else:
                                value = str(float_val)
                        except:
                            value = str(value)
                    else:
                        value = str(value) if value is not None else ""
                    item = QTableWidgetItem(value)
                    item.setFont(QFont(self.ns_font_name, 12))
                    self.table.setItem(row_idx, col_idx, item)
                    self.table.setColumnWidth(3, 250)
            self.table.resizeRowsToContents()
        else:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)

class DeliveryWidget(QWidget):
    def __init__(self, ns_font_name):
        super().__init__()
        self.ns_font_name = ns_font_name
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 날짜 2개 + 조회 버튼 한 줄
        date_row = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setFont(QFont(self.ns_font_name, 16))
        self.start_date.setFixedHeight(40)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setFont(QFont(self.ns_font_name, 16))
        self.end_date.setFixedHeight(40)

        self.search_btn = QPushButton("조회")
        self.search_btn.setFont(QFont(self.ns_font_name, 16))
        self.search_btn.setFixedHeight(40)
        self.search_btn.clicked.connect(self.on_search)

        # 엔터키로 조회 가능하게 (eventFilter 등록)
        self.start_date.installEventFilter(self)
        self.end_date.installEventFilter(self)

        date_row.addWidget(self.start_date)
        date_row.addWidget(self.end_date)
        date_row.addWidget(self.search_btn)
        date_row.addStretch()
        layout.addLayout(date_row)

        # 결과 테이블
        self.columns = [
            "주문날짜","보낸날짜","수령날짜","고객명","전화번호","탕약세기","탕약용량","탕약일수",
            "참고사항","배송방법","배송지명","수령인","수령인연락처1","수령인연락처2","배송지","주문ID","고객ID"
        ]
        self.table = QTableWidget()
        self.table.setFont(QFont(self.ns_font_name, 12))
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # ② 선택 배경색 지정
        self.table.setStyleSheet("""
                    QTableWidget::item:selected {
                        background-color: #FFD700;    /* Gold */
                        color: black;
                    }
                """)
        # 헤더 색상 스타일 적용
        self.table.horizontalHeader().setStyleSheet("""
                    QHeaderView::section,
                    QHeaderView::section:checked,
                    QHeaderView::section:pressed,
                    QHeaderView::section:focus {
                        background-color: #333333;
                        color: white;
                        font-weight: bold;
                        font-size: 20px;
                    }
                """)

        self.table.verticalHeader().setStyleSheet("""
                    QHeaderView::section {
                    background-color: 	#333333;
                    color: white;
                    font-weight: bold;
                    font-size: 20px;
                    qproperty-alignment: AlignCenter;
                    }
                """)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.on_search()

    def eventFilter(self, obj, event):
        if obj in (self.start_date, self.end_date) and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.on_search()
                return True
        return super().eventFilter(obj, event)

    def on_search(self):
        start_str = self.start_date.date().toString("yyyy-MM-dd")
        end_str = self.end_date.date().toString("yyyy-MM-dd")
        results, columns = get_delivery_table_by_period(start_str, end_str)
        self.table.clear()
        if results:
            self.table.setColumnCount(len(self.columns))
            self.table.setRowCount(len(results))
            self.table.setHorizontalHeaderLabels(self.columns)
            for row_idx, row in enumerate(results):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    item.setFont(QFont(self.ns_font_name, 12))
                    self.table.setItem(row_idx, col_idx, item)
            # 전화번호, 수령인연락처1, 수령인연락처2 컬럼 넓히기
            self.table.setColumnWidth(4, 250)   # 전화번호
            self.table.setColumnWidth(12, 250)  # 수령인연락처1
            self.table.setColumnWidth(13, 250)  # 수령인연락처2
            self.table.setColumnWidth(14, 800)  # 배송지
            self.table.resizeRowsToContents()
        else:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)


class MainWindow(QMainWindow):
    def __init__(self, ns_font_name):
        super().__init__()
        self.setWindowTitle("소담한약국 고객관리")
        self.initUI(ns_font_name)

    def initUI(self, ns_font_name):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        self.status_btn = QPushButton("현황")
        self.customer_btn = QPushButton("고객조회")
        self.delivery_btn = QPushButton("택배")

        for btn in [self.status_btn, self.customer_btn, self.delivery_btn]:
            btn.setFixedHeight(54)
            btn.setFont(QFont(ns_font_name, 18))
            btn.setStyleSheet("font-size: 22px; padding: 10px 32px;")

        button_layout.addWidget(self.status_btn)
        button_layout.addWidget(self.customer_btn)
        button_layout.addWidget(self.delivery_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.stacked = QStackedWidget()
        self.status_widget = StatusWidget(ns_font_name)
        self.customer_widget = CustomerSearchWidget(ns_font_name)
        self.delivery_widget = DeliveryWidget(ns_font_name)
        self.stacked.addWidget(self.status_widget)
        self.stacked.addWidget(self.customer_widget)
        self.stacked.addWidget(self.delivery_widget)
        main_layout.addWidget(self.stacked)

        self.status_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(0))
        self.customer_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(1))
        self.delivery_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(2))

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


# ===================== 실행부 =====================

if __name__ == "__main__":
    from PyQt5 import QtGui

    app = QApplication(sys.argv)
    #프로그램 배포시, 나눔고딕 ttf 파일을 함께 첨부
    ns_font_name = "NanumGothic"


    # DB 연결 시도, 실패하면 입력창 반복
    while True:
        try:
            conn = get_db_connection()
            conn.close()
            break
        except Exception as e:
            dlg = DbConfigDialog(DB_CONFIG['host'], DB_CONFIG['port'])
            if dlg.exec_() == QDialog.Accepted:
                host, port = dlg.get_values()
                DB_CONFIG['host'] = host #서버 IP입력(공인IP변경시 변경된 IP 입력)
                DB_CONFIG['port'] = port #서버 port입력
            else:
                QMessageBox.critical(None, "종료", "DB 서버 연결이 실패하여 프로그램을 종료합니다.")
                sys.exit(1)

    window = MainWindow(ns_font_name)
    window.showMaximized()
    sys.exit(app.exec_())