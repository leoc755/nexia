<<<<<<< HEAD
# Stellae 1.1 - Added Inline Style Support
import re

class Aurelius:
    __slots__ = ['styles']

    def __init__(self):
        self.styles = {}

    def reset(self):
        self.styles = {}

    def parse_inline(self, style_text: str) -> dict:
        """New in 1.1: Parses style='color: #f00' into a dict."""
        inline_dict = {}
        if not style_text:
            return inline_dict
            
        rules = style_text.split(';')
        for rule in rules:
            if ':' in rule:
                prop, val = rule.split(':', 1)
                p_name = prop.strip().lower()
                p_val = val.strip()
                
                # Stellae Hex Expansion
                if p_val.startswith('#') and len(p_val) == 4:
                    p_val = '#' + ''.join([c*2 for c in p_val[1:]])
                    
                inline_dict[p_name] = p_val
        return inline_dict

    def parse(self, css_text: str):
        css_blocks = re.findall(r'([^{]+)\s*\{\s*([^}]+)\}', css_text, re.S)
        for selector_group, block in css_blocks:
            selectors = [s.strip().lower() for s in selector_group.split(',')]
            for s_key in selectors:
                if s_key not in self.styles:
                    self.styles[s_key] = {}
                rules = block.split(';')
                for rule in rules:
                    if ':' in rule:
                        prop, val = rule.split(':', 1)
                        p_name, p_val = prop.strip().lower(), val.strip()
                        if p_val.startswith('#') and len(p_val) == 4:
                            p_val = '#' + ''.join([c*2 for c in p_val[1:]])
                        self.styles[s_key][p_name] = p_val

    def get_prop(self, tag: str, classes: list, element_id: str, prop: str, inline_styles: dict = None) -> str:
        """Priority: Inline (1.1) > ID > Class > Tag > Body > Universal"""
        prop = prop.lower()
        val = None
        
        # 1. Check Inline First (Highest Specificity)
        if inline_styles:
            val = inline_styles.get(prop)
        
        # 2. Global Stylesheet Lookup
        if not val and element_id:
            val = self.styles.get(f"#{element_id.lower()}", {}).get(prop)
        if not val:
            for cls in classes:
                val = self.styles.get(f".{cls.lower()}", {}).get(prop)
                if val: break
        if not val: val = self.styles.get(tag.lower(), {}).get(prop)
        if not val: val = self.styles.get("body", {}).get(prop)
        if not val: val = self.styles.get("*", {}).get(prop)
        
        if val is not None: return str(val)
        
        # Fallbacks
        if prop == "text-align": return "left"
        if prop == "font-family": return "Roboto"
=======
# Stellae 1.1 - Added Inline Style Support
import re

class Aurelius:
    __slots__ = ['styles']

    def __init__(self):
        self.styles = {}

    def reset(self):
        self.styles = {}

    def parse_inline(self, style_text: str) -> dict:
        """New in 1.1: Parses style='color: #f00' into a dict."""
        inline_dict = {}
        if not style_text:
            return inline_dict
            
        rules = style_text.split(';')
        for rule in rules:
            if ':' in rule:
                prop, val = rule.split(':', 1)
                p_name = prop.strip().lower()
                p_val = val.strip()
                
                # Stellae Hex Expansion
                if p_val.startswith('#') and len(p_val) == 4:
                    p_val = '#' + ''.join([c*2 for c in p_val[1:]])
                    
                inline_dict[p_name] = p_val
        return inline_dict

    def parse(self, css_text: str):
        css_blocks = re.findall(r'([^{]+)\s*\{\s*([^}]+)\}', css_text, re.S)
        for selector_group, block in css_blocks:
            selectors = [s.strip().lower() for s in selector_group.split(',')]
            for s_key in selectors:
                if s_key not in self.styles:
                    self.styles[s_key] = {}
                rules = block.split(';')
                for rule in rules:
                    if ':' in rule:
                        prop, val = rule.split(':', 1)
                        p_name, p_val = prop.strip().lower(), val.strip()
                        if p_val.startswith('#') and len(p_val) == 4:
                            p_val = '#' + ''.join([c*2 for c in p_val[1:]])
                        self.styles[s_key][p_name] = p_val

    def get_prop(self, tag: str, classes: list, element_id: str, prop: str, inline_styles: dict = None) -> str:
        """Priority: Inline (1.1) > ID > Class > Tag > Body > Universal"""
        prop = prop.lower()
        val = None
        
        # 1. Check Inline First (Highest Specificity)
        if inline_styles:
            val = inline_styles.get(prop)
        
        # 2. Global Stylesheet Lookup
        if not val and element_id:
            val = self.styles.get(f"#{element_id.lower()}", {}).get(prop)
        if not val:
            for cls in classes:
                val = self.styles.get(f".{cls.lower()}", {}).get(prop)
                if val: break
        if not val: val = self.styles.get(tag.lower(), {}).get(prop)
        if not val: val = self.styles.get("body", {}).get(prop)
        if not val: val = self.styles.get("*", {}).get(prop)
        
        if val is not None: return str(val)
        
        # Fallbacks
        if prop == "text-align": return "left"
        if prop == "font-family": return "Roboto"
>>>>>>> 73795b21a814b97de410b539d20b65656c9596cc
        return "undefined"