from PyQt6 import QtWidgets, uic, QtCore, QtGui
import PLC_read #Импортирование файла с классом PLC

#Класс потока для МЗС - 1, 2
class MyThread(QtCore.QThread): #Класс для создания потока состояния ПЛК
    def __init__(self, ip, state,stateTemper, stateFilter_1, stateLineEdit, cpuState, progressBar, parent=None):
        QtCore.QThread.__init__(self,  parent)
        self.running = False
        self.MZS = PLC_read.PLC(ip, 0) #10.61.105.142 - МЗС-2, 10.61.105.140 - МЗС-1/ 192.168.56.1 IP для теста в симуляторе
        self.state = state #Переменная для проверки статуса подключения
        self.stateTemper = stateTemper #Переменная для проверки температуры
        self.stateFilter_1 = stateFilter_1 #Переменная для проверки статуса фильтра
        self.stateLineEdit = stateLineEdit #Переменная для вывода Alarm
        self.cpuState = cpuState #Переменная для проверки статуса ПЛК
        #Тест для прогрессбар
        self.progressBar = progressBar
    def run(self):
        self.running = True
        self.stateLineEdit.setReadOnly(True)
        while self.running:
            self.MZS.ConnectToPLC()  # Подключение к ПЛК
            self.state(str(self.MZS.state)) #Отслеживание и запись статуса Состояния подключения
            self.stateTemper(str('{:.2f}'.format(self.MZS.ReadFrom(7, 14, 4,0)))) #Отслеживание и запись температуры гидравлики
            self.progressBar.setValue(int(self.MZS.ReadFrom(7, 14, 4, 0)))
            self.stateFilter_1(str(self.MZS.ReadFrom_Bool(16, 0, 1, 0, 3)))
            self.cpuState.setText(str(self.MZS.cpustate)) #Отслеживание ПЛК RUN/STOP

            if self.MZS.cpustate == "S7CpuStatusRun":#Изменение цвета фона в зависимости от статус ПЛК
                self.cpuState.setStyleSheet("background-color: #008000")
            else:
                self.cpuState.setStyleSheet("background-color: #FF4500")

            if self.MZS.ReadFrom_Bool(16, 0, 1, 0, 3):#Ошибка в случае нисправности фильтра 1
                self.stateLineEdit.setText('Hydraulic #1 Return Line Filter Fault')
            else:
                self.stateLineEdit.clear()
            #self.msleep(500)
        else:
            self.MZS.DisconncetToPLC()
            #self.msleep(500)

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        uic.loadUi("MyForm_test.ui", self)
        self.MZS_2 = MyThread('10.61.105.142', self.Status.setText, self.Temper.setText, self.Filter_1.setText,
                              self.lineEdit, self.cpuState, self.progressBar_2)

        self.MZS_1 = MyThread('10.61.105.140', self.Status_2.setText, self.Temper_2.setText, self.Filter_3.setText,
                              self.lineEdit_2, self.cpuState_2, self.progressBar)

        #Команды для управления МЗС-2
        self.On.clicked.connect(self.ConnectToMZS_2) #Кнопка подключиться вызывает функцию Connect
        self.Off.clicked.connect(self.DisconnectMZS_2) #Кнопка отключиться вызывает функцию Disconnect

        #Команды для управлени МЗС-1
        self.On_2.clicked.connect(self.ConnectToMZS_1)  # Кнопка подключиться вызывает функцию Connect
        self.Off_2.clicked.connect(self.DisconnectMZS_1)  # Кнопка отключиться вызывает функцию Disconnect

        self.MZS_2.finished.connect(self.finishMZS_2) #Вызов функции когда поток останавливается
        self.MZS_1.finished.connect(self.finishMZS_1)  # Вызов функции когда поток останавливается

    def ConnectToMZS_2(self): #Функция запуска потока МЗС-2
        if not self.MZS_2.isRunning():
            self.MZS_2.start() #Запуск потока
        self.On.setDisabled(True) #Блокировка кнопки пуска

    def ConnectToMZS_1(self): #Функция запуска потока МЗС-1
        if not self.MZS_1.isRunning():
            self.MZS_1.start() #Запуск потока
        self.On_2.setDisabled(True) #Блокировка кнопки пуска

    def DisconnectMZS_2(self): #Функция отключения потока МЗС-2
        self.MZS_2.running = False
        self.On.setDisabled(False)

    def DisconnectMZS_1(self): #Функция отключения потока МЗС-1
        self.MZS_1.running = False
        self.On_2.setDisabled(False)

    def finishMZS_1(self): #Отслеживание завершения потока
        self.Status_2.setText('Disconnect')
        self.Temper_2.setText('Finish')
        self.Filter_3.setText('Finish')
        self.Filter_4.setText('Finish')
        self.RecircFilter_2.setText('Finish')
        self.cpuState_2.setText('Run/Stop PLC')
        self.MZS_1.progressBar.setValue(1)

    def finishMZS_2(self): #Отслеживание завершения потока
        self.Status.setText('Disconnect')
        self.Temper.setText('Finish')
        self.Filter_1.setText('Finish')
        self.Filter_2.setText('Finish')
        self.RecircFilter.setText('Finish')
        self.cpuState.setText('Run/Stop PLC')
        self.MZS_2.progressBar.setValue(1)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())