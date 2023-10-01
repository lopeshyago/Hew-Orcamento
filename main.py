import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from layout import Ui_MainWindow  # Importe a classe gerada


class NeedleControl(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_apagar.clicked.connect(self.apagar_item)
        self.pushButton_additem.clicked.connect(self.adicionar_item)
        self.pushButton_orca.clicked.connect(self.gerar_pdf)

        self.tableWidget_prod.setColumnCount(6)
        self.tableWidget_prod.setHorizontalHeaderLabels(
            ["Descrição", "Altura (cm)", "Largura (cm)", "Quantidade", "Valor Unitário (R$)", "Total (R$)"])

        self.label_vlrpedido.setText("0.00")
        self.lineEdit_vlrfrete.setText("0.00")

        self.lineEdit_cep.textChanged.connect(self.carregar_endereco)

    def apagar_item(self):
        row_count = self.tableWidget_prod.rowCount()
        if row_count > 0:
            self.tableWidget_prod.removeRow(row_count - 1)
            self.atualizar_valor_pedido()

    def adicionar_item(self):
        descricao = self.lineEdit_desc.text()
        altura_str = self.lineEdit_alt.text().replace(',', '.')
        largura_str = self.lineEdit_larg.text().replace(',', '.')
        quantidade_str = self.lineEdit_quant.text()

        if not descricao or not altura_str or not largura_str or not quantidade_str:
            self.mostrar_mensagem_erro("Todos os campos são obrigatórios.")
            return

        try:
            altura = float(altura_str)
            largura = float(largura_str)
            quantidade = int(quantidade_str)
        except ValueError:
            self.mostrar_mensagem_erro(
                "Valores inválidos nos campos de altura, largura ou quantidade.")
            return

        custo_unitario = (altura * largura * 1.45 / 10 + 3)
        custo_total = custo_unitario * quantidade

        row_position = self.tableWidget_prod.rowCount()
        self.tableWidget_prod.insertRow(row_position)
        self.tableWidget_prod.setItem(
            row_position, 0, QTableWidgetItem(descricao))
        self.tableWidget_prod.setItem(
            row_position, 1, QTableWidgetItem(str(altura)))
        self.tableWidget_prod.setItem(
            row_position, 2, QTableWidgetItem(str(largura)))
        self.tableWidget_prod.setItem(
            row_position, 3, QTableWidgetItem(str(quantidade)))
        self.tableWidget_prod.setItem(
            row_position, 4, QTableWidgetItem(f'{custo_unitario:.2f}'))
        self.tableWidget_prod.setItem(
            row_position, 5, QTableWidgetItem(f'{custo_total:.2f}'))

        self.atualizar_valor_pedido()

    def atualizar_valor_pedido(self):
        total = 0.0
        for row in range(self.tableWidget_prod.rowCount()):
            total += float(self.tableWidget_prod.item(row, 5).text())

        self.label_vlrpedido.setText(f'{total:.2f}')

        vlr_frete_str = self.lineEdit_vlrfrete.text()
        try:
            vlr_frete = float(vlr_frete_str)
        except ValueError:
            vlr_frete = 0.0

        total_tudo = total + vlr_frete
        self.label_vlrtotal.setText(f'{total_tudo:.2f}')

    def mostrar_mensagem_erro(self, mensagem):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Erro")
        error_dialog.setText(mensagem)
        error_dialog.exec_()

    def gerar_pdf(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        save_file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF", "", "PDF Files (*.pdf)", options=options)

        if not save_file_path:
            return

        nome_cliente = self.lineEdit_nomecliente.text()
        cep = self.lineEdit_cep.text().replace('.', '')
        endereco_entrega = self.label_endentr.text()

        doc = SimpleDocTemplate(save_file_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        style_normal = styles['Normal']

        # Adicione a imagem no início do PDF
        # Substitua 'logo.png' pelo nome do seu arquivo de imagem
        imagem_logo = Image('logo.png')
        imagem_logo.drawHeight = 50  # Defina a altura da imagem conforme necessário
        imagem_logo.drawWidth = 50  # Defina a largura da imagem conforme necessário
        elements.append(imagem_logo)
        elements.append(Paragraph("<br/><br/>", style_normal))

        elements.append(
            Paragraph(f"<b>Nome do Cliente:</b>\n {nome_cliente}", style_normal))
        elements.append(Paragraph(f"<b>CEP:</b>\n {cep}", style_normal))
        elements.append(
            Paragraph(f"<b>Endereço de Entrega:</b>\n\n {endereco_entrega}", style_normal))
        # Adiciona duas linhas em branco
        elements.append(Paragraph("<br/><br/>", style_normal))

        data = [["Descrição", "Altura (cm)", "Largura (cm)",
                 "Quantidade", "Valor Uni. (R$)", "Total (R$)"]]

        for row in range(self.tableWidget_prod.rowCount()):
            descricao = self.tableWidget_prod.item(row, 0).text()
            altura = self.tableWidget_prod.item(row, 1).text()
            largura = self.tableWidget_prod.item(row, 2).text()
            quantidade = self.tableWidget_prod.item(row, 3).text()
            custo_unitario = self.tableWidget_prod.item(row, 4).text()
            custo_total = self.tableWidget_prod.item(row, 5).text()

            data.append([descricao, altura, largura, quantidade,
                        custo_unitario, custo_total])

        table = Table(data, colWidths=90, rowHeights=30)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        # Adiciona duas linhas em branco
        elements.append(Paragraph("<br/><br/>", style_normal))

        vlr_frete_str = self.lineEdit_vlrfrete.text()
        try:
            vlr_frete = float(vlr_frete_str)
        except ValueError:
            self.mostrar_mensagem_erro("Valor de Frete inválido.")
            return

        total_pedido = 0.0
        for row in range(self.tableWidget_prod.rowCount()):
            total_pedido += float(self.tableWidget_prod.item(row, 5).text())

        total_tudo = total_pedido + vlr_frete

        self.label_vlrtotal.setText(f'{total_tudo:.2f}')

        elements.append(
            Paragraph(f"<b>Valor do Frete (R$):</b> {vlr_frete:.2f}", style_normal))
        elements.append(
            Paragraph(f"<b>Valor do Pedido (R$):</b> {total_pedido:.2f}", style_normal))
        elements.append(Paragraph(
            f"<b>Valor Total Pedido + Frete (R$):</b> {total_tudo:.2f}", style_normal))

        doc.build(elements)

        self.mostrar_mensagem_informativa("PDF gerado com sucesso!")

    def mostrar_mensagem_informativa(self, mensagem):
        info_dialog = QMessageBox()
        info_dialog.setIcon(QMessageBox.Information)
        info_dialog.setWindowTitle("Informação")
        info_dialog.setText(mensagem)
        info_dialog.exec_()

    def carregar_endereco(self):
        cep = self.lineEdit_cep.text()
        numero = self.lineEdit_n.text()

        if len(cep) == 8 and numero:
            try:
                response = requests.get(
                    f'https://viacep.com.br/ws/{cep}/json/')
                data = response.json()

                if 'erro' not in data:
                    endereco = data['logradouro']
                    uf = data['uf']
                    self.label_endentr.setText(f'{endereco} {numero} - {uf}')
                else:
                    self.label_endentr.setText('CEP não encontrado')
            except requests.exceptions.RequestException:
                self.label_endentr.setText('Erro ao consultar o CEP')
        else:
            self.label_endentr.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NeedleControl()
    window.show()
    sys.exit(app.exec_())
