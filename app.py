#!/usr/bin/env python3
"""Actualiza a secção «Avaliação de Activos» do app.py do Clube APPO.
Uso:  python patch_avaliacao.py app.py        (cria app.py.bak e grava as alterações no próprio ficheiro)
Acrescenta: Preço de fecho, Valor contabilístico por acção e Diferença face ao valor justo (Kz) ao detalhe de cada empresa,
à tabela comparativa sectorial, ao Excel e à ajuda, com traduções nos 5 idiomas. Sem alterações à base de dados."""
import re, shutil, sys

ficheiro = sys.argv[1] if len(sys.argv) > 1 else "app.py"
s = open(ficheiro, encoding="utf-8").read()
shutil.copy(ficheiro, ficheiro + ".bak")


def sub(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, f"Texto esperado {n}x mas encontrado {c}x (o ficheiro difere do esperado): {old[:90]!r}"
    s = s.replace(old, new)


# 1) métricas: valor contabilístico por acção e diferença em Kz
sub('''            "ke": ke, "valor_justo": valor_justo, "upside": upside}''',
    '''            "ke": ke, "valor_justo": valor_justo, "upside": upside,
            "bvps": (bvps if bvps and bvps > 0 else None),
            "diferenca": ((valor_justo - preco) if valor_justo is not None else None)}''')

# 2) traduções (PT, EN, FR, ES, ZH — pela ordem em que aparecem no dicionário TRADUCOES)
T = [
 ('"Preço de fecho", "aval_vc": "Valor contabilístico por acção", "aval_dif": "Diferença face ao valor justo", "aval_fecho_col": "Preço de fecho (Kz)", "aval_vc_col": "Valor contab. (Kz/acção)", "aval_dif_col": "Diferença (Kz)", '
  '"aval_nota4": "<b>Preço de fecho</b> é o último preço registado. <b>Valor contabilístico</b> = capital próprio ÷ acções em circulação. <b>Diferença</b> = valor justo (DDM) − preço de fecho, em Kz: positiva sugere margem de segurança."'),
 ('"Closing price", "aval_vc": "Book value per share", "aval_dif": "Gap to fair value", "aval_fecho_col": "Closing price (Kz)", "aval_vc_col": "Book value (Kz/share)", "aval_dif_col": "Gap (Kz)", '
  '"aval_nota4": "<b>Closing price</b> is the last recorded price. <b>Book value</b> = equity ÷ shares outstanding. <b>Gap</b> = fair value (DDM) − closing price, in Kz: positive suggests a margin of safety."'),
 ('"Cours de clôture", "aval_vc": "Valeur comptable par action", "aval_dif": "Écart par rapport à la juste valeur", "aval_fecho_col": "Cours de clôture (Kz)", "aval_vc_col": "Val. comptable (Kz/action)", "aval_dif_col": "Écart (Kz)", '
  '"aval_nota4": "<b>Cours de clôture</b> = dernier prix enregistré. <b>Valeur comptable</b> = fonds propres ÷ actions en circulation. <b>Écart</b> = juste valeur (DDM) − cours de clôture, en Kz : positif suggère une marge de sécurité."'),
 ('"Precio de cierre", "aval_vc": "Valor contable por acción", "aval_dif": "Diferencia frente al valor razonable", "aval_fecho_col": "Precio de cierre (Kz)", "aval_vc_col": "Val. contable (Kz/acción)", "aval_dif_col": "Diferencia (Kz)", '
  '"aval_nota4": "<b>Precio de cierre</b> es el último precio registrado. <b>Valor contable</b> = fondos propios ÷ acciones en circulación. <b>Diferencia</b> = valor razonable (DDM) − precio de cierre, en Kz: positiva sugiere margen de seguridad."'),
 ('"收盘价", "aval_vc": "每股账面价值", "aval_dif": "与公允价值的差额", "aval_fecho_col": "收盘价（Kz）", "aval_vc_col": "每股账面价值（Kz）", "aval_dif_col": "差额（Kz）", '
  '"aval_nota4": "<b>收盘价</b>为最近记录的价格。<b>每股账面价值</b> = 净资产 ÷ 流通股数。<b>差额</b> = 公允价值（DDM）− 收盘价（Kz）：为正表示有安全边际。"'),
]
partes = s.split('"aval_nota1":')
assert len(partes) == 6, f"Esperava 5 idiomas com 'aval_nota1', encontrei {len(partes) - 1}"
novo = partes[0]
for i in range(5):
    novo += '"aval_fecho": ' + T[i] + ',\n        "aval_nota1":' + partes[i + 1]
s = novo

# 3) detalhe da empresa: cartões novos (preço de fecho, valor contabilístico por acção, diferença em Kz)
sub('''    vj, up = m["valor_justo"], m["upside"]
    kpi_linha([
        kpi_card("🎯", tx["aval_vj"]''',
    '''    _dif = m.get("diferenca")
    kpi_linha([
        kpi_card("🏷️", tx.get("aval_fecho", "Preço de fecho"), kz(av["preco"]), "último preço registado"),
        kpi_card("📖", tx.get("aval_vc", "Valor contabilístico por acção"), kz(m["bvps"]) if m.get("bvps") else "n/d",
                 ("capital próprio ÷ acções · P/BV " + multiplo(pbv)) if m.get("bvps") else "falta o capital próprio ou as acções"),
        kpi_card("↔️", tx.get("aval_dif", "Diferença face ao valor justo"), (("+" if _dif > 0 else "") + kz(_dif)) if _dif is not None else "n/d",
                 "valor justo (DDM) − preço de fecho", tom=("up" if _dif and _dif > 0 else "down" if _dif is not None and _dif < 0 else None)),
    ])
    vj, up = m["valor_justo"], m["upside"]
    kpi_linha([
        kpi_card("🎯", tx["aval_vj"]''')

# 4) tabela comparativa sectorial
sub('''    rows, xl_rows, nomes, precos, justos, ups = [], [], [], [], [], []''',
    '''    _cF = tx.get("aval_fecho_col", "Preço de fecho (Kz)")
    _cV = tx.get("aval_vc_col", "Valor contab. (Kz/acção)")
    _cD = tx.get("aval_dif_col", "Diferença (Kz)")
    rows, xl_rows, nomes, precos, justos, ups = [], [], [], [], [], []''')
sub('''        rows.append({"Empresa": r["empresa"], "Sector": r["sector"], "P/E": ml["pe"], "P/BV": ml["pbv"], "ROE": (ml["roe"] * 100) if ml["roe"] is not None else None,
                     "DY": ml["dy_nominal"] * 100, "Upside DDM": (ml["upside"] * 100) if ml["upside"] is not None else None})
        xl_rows.append([r["empresa"], r["sector"], ml["pe"], ml["pbv"], ml["roe"], ml["dy_nominal"], ml["upside"]])''',
    '''        rows.append({"Empresa": r["empresa"], "Sector": r["sector"], _cF: a["preco"], "P/E": ml["pe"], "DY": ml["dy_nominal"] * 100,
                     _cV: ml.get("bvps"), "P/BV": ml["pbv"], "ROE": (ml["roe"] * 100) if ml["roe"] is not None else None,
                     _cD: ml.get("diferenca"), "Upside DDM": (ml["upside"] * 100) if ml["upside"] is not None else None})
        xl_rows.append([r["empresa"], r["sector"], a["preco"], ml["pe"], ml["dy_nominal"], ml.get("bvps"), ml["pbv"], ml["roe"], ml.get("diferenca"), ml["upside"]])''')
sub('''        sty = num.style.format({"P/E": f("{:.1f}x"), "P/BV": f("{:.2f}x"), "ROE": f("{:.1f}%"), "DY": f("{:.1f}%"), "Upside DDM": f("{:+.1f}%")}).map(cor_variacao, subset=["Upside DDM"])
        st.dataframe(sty, hide_index=True)''',
    '''        _fkz = lambda v: "n/d" if v is None or pd.isna(v) else kz(v)
        _fdif = lambda v: "n/d" if v is None or pd.isna(v) else (("+" if v > 0 else "") + kz(v))
        sty = (num.style.format({_cF: _fkz, "P/E": f("{:.1f}x"), "DY": f("{:.1f}%"), _cV: _fkz, "P/BV": f("{:.2f}x"), "ROE": f("{:.1f}%"),
                                 _cD: _fdif, "Upside DDM": f("{:+.1f}%")})
               .map(cor_variacao, subset=[_cD, "Upside DDM"]))
        st.dataframe(sty, hide_index=True)
        st.caption(tx.get("aval_nota4", "Preço de fecho = último preço registado. Valor contabilístico = capital próprio ÷ acções. Diferença = valor justo (DDM) − preço de fecho, em Kz."))''')

# 5) Excel da comparação sectorial
sub('''    """linhas: [empresa, sector, pe, pbv, roe, dy_nominal, upside] com valores numéricos (fracções) ou None."""''',
    '''    """linhas: [empresa, sector, preço de fecho, pe, dy_nominal, valor contabilístico, pbv, roe, diferença (Kz), upside] com valores numéricos ou None."""''')
sub('''    colunas = ["Empresa", "Sector", "P/E (x)", "P/BV (x)", "ROE", "Dividend Yield nominal", "Upside DDM"]''',
    '''    colunas = ["Empresa", "Sector", "Preço de fecho (Kz)", "P/E (x)", "Dividend Yield nominal", "Valor contabilístico (Kz/acção)", "P/BV (x)", "ROE", "Diferença (Kz)", "Upside DDM"]''')
sub('''        colunas, linhas, [26, 30, 12, 12, 14, 20, 16],
        [None, None, '0.00"x"', '0.00"x"', verde_verm, '0.00%', verde_verm], folha="Comparação sectorial", cor_cond=(5, 7),''',
    '''        colunas, linhas, [26, 30, 16, 10, 14, 20, 10, 12, 16, 14],
        [None, None, '#,##0', '0.00"x"', '0.00%', '#,##0.00', '0.00"x"', verde_verm, '+#,##0;-#,##0;0', verde_verm], folha="Comparação sectorial", cor_cond=(8, 9, 10),''')
sub('''nota="P/E = preço sobre lucro; P/BV''',
    '''nota="Preço de fecho = último preço registado; valor contabilístico = capital próprio por acção; diferença = valor justo (DDM) menos preço de fecho, em Kz. P/E = preço sobre lucro; P/BV''')

# 6) ajuda «Como interpretar esta tabela»
sub('''**Upside DDM:** diferença entre o valor justo do modelo de dividendos e o preço de mercado.''',
    '''**Valor contabilístico por acção:** capital próprio ÷ acções em circulação. O preço de fecho acima deste valor dá o P/BV acima de 1x.

**Diferença (Kz):** valor justo (DDM) menos preço de fecho. Positiva = o modelo vê margem de segurança; negativa = o preço já está acima do valor estimado.

**Upside DDM:** diferença entre o valor justo do modelo de dividendos e o preço de mercado.''')

open(ficheiro, "w", encoding="utf-8").write(s)
import py_compile
py_compile.compile(ficheiro, doraise=True)
print("OK: alterações aplicadas e sintaxe verificada. Cópia de segurança em", ficheiro + ".bak")
