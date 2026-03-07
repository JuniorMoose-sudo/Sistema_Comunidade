from fpdf import FPDF


def gerar_relatorio_pdf(data_relatorio, dados):
    """Gera um PDF a partir dos dados do relatório."""

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(
                0,
                10,
                f"Relatório da Comunidade - {dados['nome_comunidade']}",
                ln=1,
                align='C',
            )
            self.set_font('Arial', '', 10)
            self.cell(
                0,
                5,
                f"Período de Referência: {data_relatorio}",
                ln=1,
                align='C',
            )
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', align='C')

    pdf = PDF()
    pdf.add_page()

    # Seção 1: Resumo Financeiro
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. Resumo Financeiro', ln=1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(
        0,
        8,
        f"  - Total de Entradas: R$ {dados['entradas_mes']:,.2f}",
        ln=1,
    )
    pdf.cell(
        0,
        8,
        f"  - Total de Saídas: R$ {dados['saidas_mes']:,.2f}",
        ln=1,
    )
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(
        0,
        8,
        f"  - Saldo do Mês: R$ {dados['saldo_mes']:,.2f}",
        ln=1,
    )
    pdf.ln(10)

    # Seção 2: Atividades da Comunidade
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. Atividades da Comunidade', ln=1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(
        0,
        8,
        f"  - Novos fiéis cadastrados no mês: {dados['novos_fieis']}",
        ln=1,
    )
    pdf.cell(
        0,
        8,
        f"  - Novos projetos iniciados no mês: {dados['novos_projetos']}",
        ln=1,
    )
    pdf.cell(
        0,
        8,
        f"  - Reuniões realizadas no mês: {dados.get('reunioes_realizadas', 0)}",
        ln=1,
    )
    pdf.ln(10)

    # Seção 3: Observações
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '3. Observações', ln=1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(
        0,
        10,
        "Este relatório foi gerado automaticamente pelo Sistema de Gestão Comunitária.",
    )

    # Garante que o conteúdo retornado seja bytes.
    output = pdf.output(dest='S')
    if isinstance(output, str):
        try:
            return output.encode('latin-1')
        except UnicodeEncodeError:
            return output.encode('utf-8')
    if isinstance(output, (bytes, bytearray)):
        return bytes(output)
    return str(output).encode('utf-8')

