"""
utils/helpers.py
Funciones auxiliares para el análisis de tiendas Alura Store
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

def configurar_estilo_graficos():
    """
    Configura el estilo visual de los gráficos
    """
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 12
    print("✅ Estilo de gráficos configurado")

def cargar_datos_tienda(ruta_archivo):
    """
    Carga los datos de una tienda desde un archivo CSV
    
    Args:
        ruta_archivo (str): Ruta al archivo CSV
    
    Returns:
        pandas.DataFrame: Datos cargados o None si hay error
    """
    try:
        datos = pd.read_csv(ruta_archivo)
        print(f"✅ Datos cargados: {len(datos)} registros - {ruta_archivo}")
        return datos
    except Exception as e:
        print(f"❌ Error cargando {ruta_archivo}: {e}")
        return None

def cargar_todas_tiendas(carpeta_data='data'):
    """
    Carga todos los archivos CSV de tiendas en la carpeta data/
    
    Args:
        carpeta_data (str): Carpeta donde están los archivos CSV
    
    Returns:
        dict: Diccionario con DataFrames de cada tienda
    """
    tiendas = {}
    
    if not os.path.exists(carpeta_data):
        print(f"❌ La carpeta '{carpeta_data}' no existe")
        return tiendas
    
    archivos = [f for f in os.listdir(carpeta_data) if f.endswith('.csv')]
    
    if not archivos:
        print(f"❌ No se encontraron archivos CSV en '{carpeta_data}'")
        return tiendas
    
    for archivo in archivos:
        nombre_tienda = archivo.replace('.csv', '').replace('tienda', 'Tienda ')
        ruta_completa = os.path.join(carpeta_data, archivo)
        tiendas[nombre_tienda] = cargar_datos_tienda(ruta_completa)
    
    print(f"📊 Se cargaron {len(tiendas)} tiendas")
    return tiendas

def generar_estadisticas_basicas(datos, nombre_tienda=""):
    """
    Genera estadísticas básicas de una tienda
    
    Args:
        datos (pandas.DataFrame): Datos de la tienda
        nombre_tienda (str): Nombre de la tienda para el reporte
    
    Returns:
        dict: Diccionario con estadísticas
    """
    if datos is None or datos.empty:
        return {}
    
    stats = {
        'tienda': nombre_tienda,
        'total_registros': len(datos),
        'total_facturacion': datos['Precio'].sum(),
        'facturacion_promedio': datos['Precio'].mean(),
        'calificacion_promedio': datos['Calificación'].mean(),
        'costo_envio_promedio': datos['Costo de envío'].mean(),
        'categorias_unicas': datos['Categoría del Producto'].nunique(),
        'productos_unicos': datos['Producto'].nunique()
    }
    
    return stats

def generar_informe_resumen(todas_tiendas):
    """
    Genera un resumen ejecutivo de todas las tiendas
    
    Args:
        todas_tiendas (dict): Diccionario con DataFrames de todas las tiendas
    
    Returns:
        pandas.DataFrame: DataFrame con resumen comparativo
    """
    resumenes = []
    
    for nombre, datos in todas_tiendas.items():
        if datos is not None:
            stats = generar_estadisticas_basicas(datos, nombre)
            resumenes.append(stats)
    
    if resumenes:
        df_resumen = pd.DataFrame(resumenes)
        return df_resumen
    else:
        return pd.DataFrame()

def crear_grafico_facturacion(resumen_tiendas, guardar=False):
    """
    Crea un gráfico de barras de facturación por tienda
    
    Args:
        resumen_tiendas (pandas.DataFrame): Resumen de tiendas
        guardar (bool): Si guardar el gráfico como imagen
    
    Returns:
        matplotlib.figure: Figura del gráfico
    """
    if resumen_tiendas.empty:
        print("❌ No hay datos para crear el gráfico")
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Ordenar por facturación
    resumen_ordenado = resumen_tiendas.sort_values('total_facturacion', ascending=False)
    
    barras = ax.bar(resumen_ordenado['tienda'], 
                   resumen_ordenado['total_facturacion'] / 1e6,  # Convertir a millones
                   color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'])
    
    ax.set_title('Facturación Total por Tienda (en millones)', fontweight='bold')
    ax.set_ylabel('Facturación (Millones $)')
    ax.tick_params(axis='x', rotation=45)
    
    # Añadir valores en las barras
    for bar in barras:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}M', ha='center', va='bottom')
    
    plt.tight_layout()
    
    if guardar:
        os.makedirs('outputs/graficos_analisis', exist_ok=True)
        plt.savefig('outputs/graficos_analisis/facturacion_tiendas.png', dpi=300, bbox_inches='tight')
        print("✅ Gráfico guardado: outputs/graficos_analisis/facturacion_tiendas.png")
    
    return fig

def exportar_resumen_csv(resumen_tiendas, nombre_archivo='resumen_tiendas.csv'):
    """
    Exporta el resumen a un archivo CSV
    
    Args:
        resumen_tiendas (pandas.DataFrame): Resumen a exportar
        nombre_archivo (str): Nombre del archivo de salida
    """
    if resumen_tiendas.empty:
        print("❌ No hay datos para exportar")
        return
    
    os.makedirs('outputs', exist_ok=True)
    ruta_completa = os.path.join('outputs', nombre_archivo)
    resumen_tiendas.to_csv(ruta_completa, index=False, encoding='utf-8')
    print(f"✅ Resumen exportado: {ruta_completa}")

def analizar_categorias(datos_tienda, nombre_tienda=""):
    """
    Analiza las categorías de productos de una tienda
    
    Args:
        datos_tienda (pandas.DataFrame): Datos de la tienda
        nombre_tienda (str): Nombre de la tienda
    
    Returns:
        pandas.DataFrame: Resumen por categoría
    """
    if datos_tienda is None or datos_tienda.empty:
        return pd.DataFrame()
    
    resumen_categorias = datos_tienda.groupby('Categoría del Producto').agg({
        'Precio': ['sum', 'mean', 'count'],
        'Calificación': 'mean',
        'Costo de envío': 'mean'
    }).round(2)
    
    # Aplanar columnas multiindex
    resumen_categorias.columns = ['facturacion_total', 'precio_promedio', 
                                 'cantidad_productos', 'calificacion_promedio', 
                                 'costo_envio_promedio']
    
    resumen_categorias = resumen_categorias.sort_values('facturacion_total', ascending=False)
    
    print(f"📊 Análisis de categorías para {nombre_tienda}:")
    print(f"   - Total categorías: {len(resumen_categorias)}")
    print(f"   - Categoría líder: {resumen_categorias.index[0]}")
    
    return resumen_categorias

# Función para probar que el módulo funciona
def probar_modulo():
    """Función para probar que el módulo se carga correctamente"""
    print("🔄 Probando módulo helpers...")
    configurar_estilo_graficos()
    print("✅ Módulo helpers cargado correctamente")

if __name__ == "__main__":
    probar_modulo()
