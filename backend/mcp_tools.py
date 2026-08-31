"""
Skills & MCP Tools Module for Horizon Academy AI Assistant.
Provides specialized business logic calculations for tuition, discounts, and level structures.
"""

def calculate_tuition_fee(num_modules: int = 1, include_matricula: bool = False, pronto_pago: bool = False) -> str:
    """
    Skill: Calculates exact tuition fees, discounts, and total COP for Horizon Academy.
    - Base module cost: $480.000 COP
    - Matrícula (one-time): $60.000 COP
    - Trimodular discount (3+ modules): 10%
    - Pronto pago discount: 5%
    """
    base_module_price = 480000
    matricula_price = 60000 if include_matricula else 0
    
    total_modules_base = num_modules * base_module_price
    discount_text = ""
    discount_amount = 0
    
    if num_modules >= 3:
        discount_amount = total_modules_base * 0.10
        discount_text = " (Aplica 10% de descuento por Paquete Trimodular)"
    elif pronto_pago:
        discount_amount = total_modules_base * 0.05
        discount_text = " (Aplica 5% de descuento por Pronto Pago)"

    final_modules_total = total_modules_base - discount_amount
    grand_total = final_modules_total + matricula_price
    
    res = f"Para {num_modules} módulo(s): Subtotal módulos: ${total_modules_base:,.0f} COP."
    if discount_amount > 0:
        res += f" Descuento aplicado: ${discount_amount:,.0f} COP{discount_text}."
    if include_matricula:
        res += f" Matrícula inicial: $60.000 COP."
    res += f" Total final a pagar: ${grand_total:,.0f} COP."
    return res

def get_skills_instructions() -> str:
    """
    Returns skills rules to inject into the system prompt for dynamic calculation tasks.
    """
    return """
HERRAMIENTAS DE CÁLCULO Y SKILLS ACTIVAS (Úsalas para realizar cálculos y tareas numéricas sobre la documentación):
1. Skill de Cálculo de Tarifas y Descuentos:
   - Valor módulo bimestral (2 meses): $480.000 COP.
   - Matrícula inicial (pago único por programa): $60.000 COP.
   - Si el usuario pregunta por 3 o más módulos (Paquete Trimodular), aplica un 10% de descuento sobre el valor de los módulos.
   - Si pregunta por Pronto Pago, aplica 5% de descuento sobre el módulo.
2. Skill de Duración y Horas de Niveles:
   - Niveles A1, A2 y C1: 2 módulos bimestrales (4 meses en total, 80h guiadas + 40h autónomas).
   - Niveles B1 y B2: 3 módulos bimestrales (6 meses en total, 120h guiadas + 60h autónomas).
   - Cada submódulo bimestral equivale a 40 horas lectivas guiadas + 20 horas de trabajo autónomo.
"""
