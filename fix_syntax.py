#!/usr/bin/env python3

# Fix syntax error in medequity_main.py
with open('medequity_main.py', 'r') as f:
    content = f.read()

# Fix the indentation issue in display_ultra_market_overview
content = content.replace(
    '''        try:
            stock = yf.Ticker(etf)
        info = stock.info''',
    '''        try:
            stock = yf.Ticker(etf)
            info = stock.info'''
)

# Fix any other indentation issues
content = content.replace(
    '''    except:
            st.markdown''',
    '''        except:
            st.markdown'''
)

# Also fix the for loop indentation in create_ultra_stock_grid
content = content.replace(
    '''    for i, (category, stocks) in enumerate(stock_categories.items()):
                with cols[i]:''',
    '''    for i, (category, stocks) in enumerate(stock_categories.items()):
        with cols[i]:'''
)

# Add critical CSS for layout fixing at the top
css_fix = '''    /* CRITICAL LAYOUT FIXES */
    .main .block-container {
        max-width: 100% !important;
        padding: 1rem 2rem !important;
        margin: 0 auto !important;
        width: 100% !important;
    }
    
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .element-container {
        width: 100% !important;
        max-width: none !important;
    }
    
    /* Center content properly */
    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
        margin: 0 auto !important;
        width: 100% !important;
    }
    
    '''

# Insert the critical CSS after the first CSS variable definitions
content = content.replace(
    '    /* Enhanced spacing system - MAJOR FIX */',
    css_fix + '\n    /* Enhanced spacing system - MAJOR FIX */'
)

with open('medequity_main.py', 'w') as f:
    f.write(content)

print("✅ Fixed syntax errors and layout issues!") 