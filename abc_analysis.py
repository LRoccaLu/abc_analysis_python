import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# Función para aplicar el método ABC
def aplicar_metodo_abc(df):
    """
    Clasificación ABC basada en un valor ponderado que combina:
    - Frecuencia de uso
    - Costo de mantenimiento
    - Valor de reposición
    """
    df['Valor'] = df['Frecuencia de Uso'] * df['Costo de Mantenimiento'] + df['Valor de Reposición']
    df = df.sort_values(by='Valor', ascending=False)
    df['Valor Acumulado'] = df['Valor'].cumsum()
    df['Porcentaje Acumulado'] = 100 * df['Valor Acumulado'] / df['Valor'].sum()
    df['Clasificación ABC'] = df['Porcentaje Acumulado'].apply(
        lambda x: 'A' if x <= 80 else ('B' if x <= 95 else 'C')
    )
    return df

# Función para generar el gráfico ABC
def graficar_abc(df, output_dir):
    conteo_abc = df['Clasificación ABC'].value_counts().sort_index()
    plt.figure(figsize=(8, 6))
    plt.bar(conteo_abc.index, conteo_abc.values)
    plt.title('Distribución de activos por clasificación ABC')
    plt.xlabel('Clasificación ABC')
    plt.ylabel('Cantidad de activos')

    for i, value in enumerate(conteo_abc.values):
        plt.text(i, value + 0.5, f'{value}', ha='center')

    image_path = os.path.join(output_dir, 'grafico_abc.png')
    plt.tight_layout()
    plt.savefig(image_path)
    plt.show()

    return image_path

# Clase para generar el PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Informe de Análisis ABC de Activos', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 8, body)
        self.ln()

    def add_table(self, df):
        self.set_font('Arial', '', 8)
        self.ln(5)
        for col in df.columns:
            self.cell(35, 8, col, 1, 0, 'C')
        self.ln()
        for _, row in df.iterrows():
            for value in row:
                self.cell(35, 8, str(round(value, 2)) if isinstance(value, float) else str(value), 1, 0, 'C')
            self.ln()

# Función principal
def main():
    num_activos = int(input("¿Cuántos activos desea analizar?: "))
    data = []

    for i in range(num_activos):
        print(f"\nActivo {i + 1}:")
        nombre = input("Nombre del activo: ")
        frecuencia = float(input("Frecuencia de uso (horas/mes): "))
        costo = float(input("Costo de mantenimiento: "))
        reposicion = float(input("Valor de reposición: "))
        fallos = float(input("Tasa de fallos (mensual): "))
        data.append([nombre, frecuencia, costo, reposicion, fallos])

    df = pd.DataFrame(
        data,
        columns=[
            'Activo',
            'Frecuencia de Uso',
            'Costo de Mantenimiento',
            'Valor de Reposición',
            'Tasa de Fallos'
        ]
    )

    df_abc = aplicar_metodo_abc(df)
    print("\nResultado del análisis ABC:")
    print(df_abc)

    # Directorio del script
    output_dir = os.path.dirname(os.path.abspath(__file__))

    image_path = graficar_abc(df_abc, output_dir)

    pdf = PDF(orientation='L')
    pdf.add_page()

    pdf.chapter_title('Resumen')
    pdf.chapter_body(
        'Este informe presenta un análisis ABC aplicado a un conjunto de activos, '
        'utilizando un criterio ponderado para apoyar la priorización de mantenimiento '
        'y la toma de decisiones operativas.'
    )

    pdf.chapter_title('Resultados del Análisis ABC')
    pdf.add_table(df_abc)

    pdf.chapter_title('Gráfico de Clasificación ABC')
    pdf.image(image_path, x=20, w=240)

    pdf_path = os.path.join(output_dir, 'informe_analisis_abc.pdf')
    pdf.output(pdf_path)

    print(f'\nInforme generado correctamente: {pdf_path}')

if __name__ == "__main__":
    main()
