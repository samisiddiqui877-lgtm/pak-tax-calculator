import gradio as gr

# --- Tax Slab Data ---
# Key: The ceiling amount for the slab (or 'over' for the highest slab).
# Value: A tuple (Fixed Tax Amount, Marginal Rate, Exceeding Amount)
TAX_SLABS = {
    600000: (0, 0, 0),
    1200000: (0, 0.01, 600000),
    2200000: (6000, 0.11, 1200000),
    3200000: (116000, 0.23, 2200000),
    4100000: (346000, 0.30, 3200000),
    'over': (616000, 0.35, 4100000)
}

def calculate_taxable_income(
    basic_salary_m, hra_m, conveyance_m, medical_m, other_m,
    utility_m, special_m, bonus_m, overtime_m, tada_m, 
    housing_m, education_m, leave_encashment_m, food_m, commission_m, misc_bonus_m, 
    employer_pf_a
):
    """Calculates the total Annual Taxable Income based on 16 monthly inputs and 1 annual input."""
    
    # 1. Annualize Monthly Components (All 16 components are summed up)
    total_monthly_components = (
        basic_salary_m + hra_m + conveyance_m + medical_m + other_m +
        utility_m + special_m + bonus_m + overtime_m + tada_m +
        housing_m + education_m + leave_encashment_m + food_m + commission_m + misc_bonus_m
    )
    annual_income = total_monthly_components * 12
    
    # 2. Calculate Taxable Income (including Employer PF contribution)
    total_taxable_income = annual_income + employer_pf_a
    
    return total_taxable_income

def calculate_annual_tax(taxable_income):
    """Calculates the Annual Tax based on the provided tax slabs."""
    
    for ceiling, (fixed_tax, rate, exceeding_amount) in TAX_SLABS.items():
        if ceiling == 'over':
            if taxable_income > exceeding_amount:
                taxable_amount_over_limit = taxable_income - exceeding_amount
                annual_tax = fixed_tax + (taxable_amount_over_limit * rate)
                slab_info = f"S#6 (Over Rs. {exceeding_amount:,})"
                return annual_tax, slab_info, fixed_tax, rate, exceeding_amount, taxable_amount_over_limit
            break
                
        elif taxable_income <= ceiling:
            taxable_amount_over_limit = taxable_income - exceeding_amount
            
            if exceeding_amount == 0:
                # S#1: Not exceeding 600,000 (Tax is 0)
                annual_tax = 0
                slab_info = f"S#1 (Upto Rs. {ceiling:,})"
                
            elif exceeding_amount == 600000:
                # S#2: Exceeding 600,000 but not 1,200,000
                annual_tax = taxable_amount_over_limit * rate
                slab_info = f"S#2 (Rs. {exceeding_amount:,} to Rs. {ceiling:,})"
                
            else:
                # S#3, S#4, S#5
                annual_tax = fixed_tax + (taxable_amount_over_limit * rate)
                # Find the slab number dynamically
                slab_index = list(TAX_SLABS.keys()).index(ceiling) + 1
                slab_info = f"S#{slab_index} (Rs. {exceeding_amount:,} to Rs. {ceiling:,})"
                
            return annual_tax, slab_info, fixed_tax, rate, exceeding_amount, taxable_amount_over_limit
    
    return 0, "Not Found", 0, 0, 0, 0

def run_tax_calculator_web(
    basic_salary_m, hra_m, conveyance_m, medical_m, other_m, 
    utility_m, special_m, bonus_m, overtime_m, tada_m,
    housing_m, education_m, leave_encashment_m, food_m, commission_m, misc_bonus_m, 
    employer_pf_a
):
    """Web-friendly function to collect inputs, calculate, and display results/steps."""
    
    # Define the link to be added
    fbr_link = "https://share.google/5QbLZn6MdDWtL43xT"
    
    # Ensure all 17 inputs are treated as numbers
    try:
        inputs = [
            basic_salary_m, hra_m, conveyance_m, medical_m, other_m,
            utility_m, special_m, bonus_m, overtime_m, tada_m,
            housing_m, education_m, leave_encashment_m, food_m, commission_m, misc_bonus_m, 
            employer_pf_a
        ]
        inputs = [float(i) for i in inputs]
    except (ValueError, TypeError):
        return ("**Error:** Please ensure all fields contain valid numbers.","","","")
        
    # Unpack all 17 inputs
    basic_salary_m, hra_m, conveyance_m, medical_m, other_m, \
    utility_m, special_m, bonus_m, overtime_m, tada_m, \
    housing_m, education_m, leave_encashment_m, food_m, commission_m, misc_bonus_m, \
    employer_pf_a = inputs

    # --- Calculation Steps ---
    annual_taxable_income = calculate_taxable_income(
        basic_salary_m, hra_m, conveyance_m, medical_m, other_m,
        utility_m, special_m, bonus_m, overtime_m, tada_m,
        housing_m, education_m, leave_encashment_m, food_m, commission_m, misc_bonus_m,
        employer_pf_a
    )
    
    annual_tax, slab_info, fixed_tax, rate, exceeding_amount, taxable_amount_over_limit = calculate_annual_tax(
        annual_taxable_income
    )
    
    monthly_tax = annual_tax / 12
    
    # --- Output Summary ---
    summary = f"""
    ### 💰 Calculated Tax Summary ###
    | Metric | Value |
    | :--- | :--- |
    | **Annual Taxable Income** | Rs. {annual_taxable_income:,.2f} |
    | **Annual Tax** | **Rs. {annual_tax:,.2f}** |
    | **Monthly Tax** | **Rs. {monthly_tax:,.2f}** |
    """
    
    # --- Step-by-Step Guide ---
    steps = "\n### 📝 Step-by-Step Guide ###\n"
    
    # Step 1: Calculate Gross Annual Salary from all 16 monthly inputs
    total_monthly_income = (
        basic_salary_m + hra_m + conveyance_m + medical_m + other_m +
        utility_m + special_m + bonus_m + overtime_m + tada_m +
        housing_m + education_m + leave_encashment_m + food_m + commission_m + misc_bonus_m
    )
    gross_annual_salary = total_monthly_income * 12
    steps += "**STEP 1: Calculate Annual Taxable Income**\n"
    steps += f"Gross Annual Salary (16 components * 12): Rs. {gross_annual_salary:,.2f}\n"
    steps += f"Annual Taxable Income (Gross Salary + Employer PF): **Rs. {annual_taxable_income:,.2f}**\n"
    
    # Step 2 & 3
    steps += "\n**STEP 2 & 3: Apply Tax Slab and Calculate Annual Tax**\n"
    steps += f"Applicable Slab: **{slab_info}**\n"
    
    if annual_tax == 0 and annual_taxable_income <= 600000:
        steps += "Annual Tax: 0% as income does not exceed Rs. 600,000.\n"
    elif exceeding_amount == 600000 and fixed_tax == 0:
        # S#2
        tax_calc_text = f"1% of (Rs. {annual_taxable_income:,.2f} - Rs. 600,000) = **Rs. {annual_tax:,.2f}**"
        steps += f"Annual Tax Calculation: {tax_calc_text}\n"
    elif fixed_tax > 0:
        # S#3 to S#6
        tax_rate_percent = int(rate*100)
        marginal_tax = taxable_amount_over_limit * rate
        tax_calc_text = f"Fixed Tax (Rs. {fixed_tax:,.2f}) + {tax_rate_percent}% of excess (Rs. {taxable_amount_over_limit:,.2f} x {rate} = Rs. {marginal_tax:,.2f})"
        steps += f"Annual Tax Calculation: {tax_calc_text}\n"
        steps += f"Total Annual Tax: **Rs. {annual_tax:,.2f}**\n"
        
    # Step 4
    steps += "\n**STEP 4: Calculate Monthly Tax**\n"
    steps += f"Monthly Tax: Rs. {annual_tax:,.2f} / 12 = **Rs. {monthly_tax:,.2f}**\n"
    
    # --- Tax Filing Assistant ---
    assistant = "\n## 💡 Tax Filing Assistant & Next Steps ##\n"
    # 1. Action based on Tax Amount
    if monthly_tax > 0:
        assistant += f"* **Verify TDS:** Check your payslips to ensure your employer deducts **Rs. {monthly_tax:,.2f}** (Tax Deducted at Source).\n"
    else:
        assistant += "* **No Tax Liability:** Your income falls below the minimum taxable limit (Rs. 600,000).\n"
        
    # 2. Filing Obligation
    if annual_taxable_income >= 600000:
        assistant += "* **Mandatory Filing:** Since your income is above Rs. 600,000, you are legally required to file an annual income tax return with the FBR.\n"
    
    # 3. FBR Portal
    # LINK IS INCLUDED HERE
    assistant += f"* **FBR Portal:** The filing is done electronically via the **[FBR Iris Portal]({fbr_link})**.\n"
    
    # 4. General Advice
    disclaimer = "\n**General Advice:** Always consult the official FBR income tax ordinance and a qualified tax professional for your specific filing needs."
    return summary, steps, assistant, disclaimer

# --- Gradio Interface Setup ---
# Define the inputs for the Gradio interface
monthly_income_inputs = [
    # Group 1: Standard
    gr.Number(label="1. Basic Salary (Monthly): Rs.", value=0),
    gr.Number(label="2. House Rent Allowance (HRA) (Monthly): Rs.", value=0),
    gr.Number(label="3. Conveyance Allowance (Monthly): Rs.", value=0),
    gr.Number(label="4. Medical Allowance (Monthly): Rs.", value=0),
    gr.Number(label="5. Other General Allowance (Monthly): Rs.", value=0),
    
    # Group 2: Common Extras
    gr.Number(label="6. Utility Allowance (Monthly): Rs.", value=0),
    gr.Number(label="7. Special/Technical Allowance (Monthly): Rs.", value=0),
    gr.Number(label="8. Performance/Ad-hoc Bonus (Monthly Avg): Rs.", value=0),
    gr.Number(label="9. Overtime (Monthly Avg): Rs.", value=0),
    gr.Number(label="10. TADA/Daily Allowance (Monthly Avg): Rs.", value=0),
    
    # Group 3: Specific/Less Common (Totaling 16)
    gr.Number(label="11. Housing/Accommodation Allowance (Monthly): Rs.", value=0),
    gr.Number(label="12. Education/Children Allowance (Monthly): Rs.", value=0),
    gr.Number(label="13. Leave Encashment (Monthly Avg): Rs.", value=0),
    gr.Number(label="14. Food/Meal Allowance (Monthly): Rs.", value=0),
    gr.Number(label="15. Commission/Incentive (Monthly Avg): Rs.", value=0),
    gr.Number(label="16. Miscellaneous Bonus/Receipt (Monthly Avg): Rs.", value=0),
]

annual_input = gr.Number(label="17. Employer's PF Contribution (Annual): Rs.", value=0)

# Combine inputs (16 Monthly + 1 Annual)
all_inputs = monthly_income_inputs + [annual_input]

# Define the outputs (Markdown for rich text display)
outputs = [
    gr.Markdown(label="Tax Summary"),
    gr.Markdown(label="Calculation Steps"),
    gr.Markdown(label="Filing Assistant"),
    gr.Markdown(label="Disclaimer"),
]

# Create the Gradio interface
iface = gr.Interface(
    fn=run_tax_calculator_web,
    inputs=all_inputs,
    outputs=outputs,
    title="💰 Pakistan Salaried Income Tax Calculator (16 Monthly Inputs)",
    description="Enter your 16 monthly salary components and annual Employer PF contribution to calculate the applicable income tax based on FBR tax slabs.",
)

# Launch the interface
if __name__ == "__main__":
    iface.launch()
