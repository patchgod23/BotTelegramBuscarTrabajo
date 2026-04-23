def calculate_ranking(title, keywords_dict):
    score = 0
    title_lower = title.lower()
    
    matched_kws = []
    modifiers = {"junior", "trainee", "sin experiencia"}
    
    for kw, weight in keywords_dict.items():
        if kw.lower() in title_lower:
            score += weight
            matched_kws.append(kw.lower())
            
    if matched_kws:
        # Si TODAS las palabras que hicieron match son solo modificadores (ej. un "Mecánico Junior")
        # entonces descartamos la oferta asignándole puntaje 0.
        all_modifiers = all(kw in modifiers for kw in matched_kws)
        if all_modifiers:
            return 0
            
    return score
