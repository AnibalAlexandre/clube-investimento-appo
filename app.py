"""
Testes dos fluxos financeiros, permissões e privacidade do app.py do Clube APPO.

NUNCA corra isto contra a base de dados real. Use uma base de teste vazia, por exemplo:
    export APPO_TEST_DATABASE_URL=postgresql://utilizador:palavra@localhost/appo_test
    python tests/test_appo.py
O script recusa-se a correr se o nome da base de dados não contiver "test".
Requer: pip install psycopg2-binary bcrypt pandas fpdf2 requests
Os testes usam um substituto mínimo do Streamlit (não abrem a interface).
"""
import os, sys, types, threading, traceback, warnings
warnings.filterwarnings('ignore')
from datetime import date, datetime, timedelta
from decimal import Decimal

URL = os.environ.get("APPO_TEST_DATABASE_URL", "")
if not URL or "test" not in URL.rsplit("/", 1)[-1].lower():
    sys.exit("Defina APPO_TEST_DATABASE_URL para uma base de dados de TESTE (o nome tem de conter 'test').")
os.environ["DATABASE_URL"] = URL


class SS(dict):
    __getattr__ = dict.get
    def __setattr__(self, k, v): self[k] = v


class Any:
    def __call__(self, *a, **k): return Any()
    def __getattr__(self, n): return Any()
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def __iter__(self): return iter([Any() for _ in range(8)])
    def __bool__(self): return False


def _cache(*a, **k):
    if a and callable(a[0]) and not k:
        f = a[0]; f.clear = lambda *x, **y: None; return f
    def deco(f): f.clear = lambda *x, **y: None; return f
    return deco


def carregar(path=None):
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app.py")
    st = types.ModuleType("streamlit")
    st.session_state = SS(); st.cache_resource = _cache; st.cache_data = _cache
    st.__getattr__ = lambda n: Any(); st.sidebar = Any()
    sys.modules["streamlit"] = st
    for nome in ("streamlit.components", "streamlit.components.v1"):
        m = types.ModuleType(nome); m.html = lambda *a, **k: None; sys.modules[nome] = m
    src = open(path, encoding="utf-8").read()
    corte = src.index("\n# =========================================================\n# AUTENTICAÇÃO")
    ns = {"__name__": "appo_test"}
    exec(compile(src[:corte], path, "exec"), ns)
    ns["_st"] = st
    return ns


ns = carregar()
st = ns["_st"]
executar, consultar_um, consultar_df = ns["executar"], ns["consultar_um"], ns["consultar_df"]
D = Decimal


def papel(admin=False, participante=False, email="admin@teste.ao"):
    st.session_state.clear()
    st.session_state.update({"autenticado": True, "is_admin": admin, "is_participante": participante, "conta_email": email})


def limpar():
    for t in ("unidades_movimentos", "balanco_privado", "auditoria", "historico_vup", "carteira_real", "pedidos_servicos",
              "manifestacoes_interesse", "despesas_admin", "identidades_socios"):
        executar(f"DELETE FROM {t}")
    executar("UPDATE cotas_config SET unidades_base_validada = FALSE, data_base = NULL, fundamento_base = NULL, limite_cotas = 0, entrada_minima = 0, valor_nominal = 100000 WHERE id = 1")
    executar("DELETE FROM activos")
    for nome, tk, preco in (("BAI (ACÇÃO)", "BAIAAAAA", 94600), ("BFA (ACÇÃO)", "BFAAAAA", 98000), ("UNITEL (ACÇÃO)", "UNTLAAAA", 30600), ("Standard Bank (ACÇÃO)", "SBAOAAAA", 65000)):
        executar("INSERT INTO activos (nome, tipo, preco, variacao, ticker) VALUES (%s, 'ACÇÃO', %s, 0, %s)", (nome, preco, tk))
    for tk, nome, q, custo in (("BAIAAAAA", "Acção BAI", 4, 362031.48), ("BFAAAAAA", "Acção BFA", 4, 386166.92),
                               ("SBAOAAAA", "Acção Standard Bank", 16, 806794.40), ("UNTLAAAA", "Acção Unitel", 38, 1311562.53)):
        executar("INSERT INTO carteira_real (ticker, nome, qtd, valor_aquisicao) VALUES (%s, %s, %s, %s)", (tk, nome, q, custo))


FUNDADORES = [{"Sócio": "Aníbal Alexandre Pereira da Costa", "E-mail da conta (opcional)": "admin@teste.ao", "% do capital": 55.0},
              {"Sócio": "Fundador II", "E-mail da conta (opcional)": "", "% do capital": 15.0},
              {"Sócio": "Fundador III", "E-mail da conta (opcional)": "", "% do capital": 10.0},
              {"Sócio": "Fundador IV", "E-mail da conta (opcional)": "", "% do capital": 10.0},
              {"Sócio": "Fundador V", "E-mail da conta (opcional)": "", "% do capital": 10.0}]


def preparar_base_validada():
    """Balanço validado + estrutura inicial adoptada e reconciliada."""
    papel(admin=True)
    ns["registar_balanco"](date.today(), 2014073.93, 0, 0, "Extracto do homebroker (teste)", "Conta pessoal do administrador (teste)", "Validado")
    linhas = ns["calcular_subscricoes_iniciais"](4866555, 100000, FUNDADORES)
    ns["adoptar_estrutura_inicial"](linhas, 100000, date.today(), "Acta de teste", True)


RESULTADOS = []


def teste(f):
    try:
        limpar(); f(); RESULTADOS.append((f.__name__, "OK", ""))
    except Exception as e:
        RESULTADOS.append((f.__name__, "FALHOU", "".join(traceback.format_exception_only(type(e), e)).strip()))
    return f


def levanta(exc, f, *a, **k):
    try:
        f(*a, **k)
    except exc as e:
        return str(e)
    raise AssertionError(f"Esperava {exc.__name__}")


@teste
def migracao_idempotente():
    ns["inicializar_bd"]()
    ns["inicializar_bd"]()


@teste
def permissoes_visitante_cliente_participante_admin():
    st.session_state.clear()                     # visitante: sem sessão
    levanta(PermissionError, ns["obter_vup_info"])
    levanta(PermissionError, ns["obter_carteira_real"])
    papel(admin=False, participante=False, email="aluno@teste.ao")   # cliente/aluno
    levanta(PermissionError, ns["obter_vup_info"])
    levanta(PermissionError, ns["obter_unidades_movimentos"])
    levanta(PermissionError, ns["registar_balanco"], date.today(), 1, 0, 0, "x", "y")
    papel(admin=False, participante=True, email="part@teste.ao")      # participante não-admin
    ns["obter_vup_info"]()
    levanta(PermissionError, ns["registar_balanco"], date.today(), 1, 0, 0, "x", "y")
    levanta(PermissionError, ns["anular_movimento_unidades"], 1, "x")
    papel(admin=True)
    ns["obter_vup_info"]()


@teste
def vup_nao_calculado_sem_dados_essenciais():
    papel(admin=True)
    i = ns["obter_vup_info"]()
    assert i["estado"] == "Não calculado" and i["vup"] == 0 and i["motivos"], i


@teste
def vup_calculo_decimal_e_estados():
    papel(admin=True)
    ns["registar_balanco"](date.today(), 2014073.93, 0, 0, "Extracto", "Conta pessoal (teste)", "Provisório")
    linhas = ns["calcular_subscricoes_iniciais"](4866555, 100000, FUNDADORES)
    assert sum(l["montante"] for l in linhas) == D("4866555.00"), "o total tem de bater certo"
    ns["adoptar_estrutura_inicial"](linhas, 100000, date.today(), "Acta de teste", False)
    i = ns["obter_vup_info"]()
    esperado_nav = D("2973200") + D("2014073.93")                      # carteira a preços da app + dinheiro
    assert i["nav"] == esperado_nav, (i["nav"], esperado_nav)           # capital realizado NÃO entra
    assert i["estado"] == "Provisório", i["estado"]                     # balanço e base ainda não validados
    unidades = sum(l["cotas"] for l in linhas)
    assert abs(i["vup_dec"] - (esperado_nav / unidades)) < D("0.0001")
    ns["definir_base_reconciliada"](True, "teste")
    ns["validar_balanco"](ns["obter_ultimo_balanco"]()[0], "teste")
    assert ns["obter_vup_info"]()["estado"] == "Validado"
    levanta(ValueError, ns["adoptar_estrutura_inicial"], linhas, 100000, date.today(), "outra", True)   # só uma vez


@teste
def subscricao_nao_altera_vup_e_actualiza_caixa():
    preparar_base_validada()
    antes = ns["obter_vup_info"]()
    r = ns["registar_operacao_unidades"]("Subscrição", "Novo Participante", None, 500000, "Ordinária", date.today(), "T-001")
    depois = ns["obter_vup_info"]()
    assert r["unidades"] == ns["q6"](D(500000) / antes["vup_dec"])
    assert abs(depois["vup_dec"] - antes["vup_dec"]) < D("0.01"), (antes["vup_dec"], depois["vup_dec"])
    assert D(str(depois["dinheiro"])) == D(str(antes["dinheiro"])) + 500000        # caixa e unidades na mesma transacção
    assert abs(depois["unidades"] - (antes["unidades"] + float(r["unidades"]))) < 1e-6
    n = consultar_um("SELECT COUNT(*) FROM auditoria WHERE accao = 'Subscrição de unidades'")[0]
    assert n == 1
    mov = consultar_um("SELECT antes, depois, criado_por, referencia FROM unidades_movimentos WHERE referencia = 'T-001'")
    assert mov[0] and mov[1] and mov[2] == "admin@teste.ao"                        # retrato anterior e posterior


@teste
def duplicacao_bloqueada_pela_referencia():
    preparar_base_validada()
    ns["registar_operacao_unidades"]("Subscrição", "Novo", None, 100000, "Ordinária", date.today(), "DUP-1")
    levanta(ValueError, ns["registar_operacao_unidades"], "Subscrição", "Novo", None, 100000, "Ordinária", date.today(), "DUP-1")
    assert consultar_um("SELECT COUNT(*) FROM unidades_movimentos WHERE referencia = 'DUP-1'")[0] == 1


@teste
def retroactivo_exige_vup_historico_e_fundamento():
    preparar_base_validada()
    ontem = date.today() - timedelta(days=30)
    levanta(ValueError, ns["registar_operacao_unidades"], "Subscrição", "Novo", None, 100000, "Ordinária", ontem, "RET-1")
    r = ns["registar_operacao_unidades"]("Subscrição", "Novo", None, 100000, "Ordinária", ontem, "RET-2",
                                         fundamento="Regularização documentada (teste)", vup_historico=D("98000"))
    assert r["origem"] == "Regularização" and r["vup"] == D("98000.0000")
    levanta(ValueError, ns["registar_operacao_unidades"], "Subscrição", "Novo", None, 100000, "Ordinária",
            date.today() + timedelta(days=2), "FUT-1")


@teste
def limites_entrada_minima_resgate_e_liquidez():
    preparar_base_validada()
    executar("UPDATE cotas_config SET entrada_minima = 100000, limite_cotas = 50 WHERE id = 1")
    levanta(ValueError, ns["registar_operacao_unidades"], "Subscrição", "A", None, 50000, "Ordinária", date.today(), "MIN-1")    # abaixo do mínimo
    levanta(ValueError, ns["registar_operacao_unidades"], "Subscrição", "A", None, 500000, "Ordinária", date.today(), "LIM-1")    # passa o limite
    executar("UPDATE cotas_config SET limite_cotas = 0 WHERE id = 1")
    levanta(ValueError, ns["registar_operacao_unidades"], "Resgate", "Fundador II", None, 9999999, "Fundadora", date.today(), "RES-1")  # mais do que tem / sem liquidez
    levanta(ValueError, ns["registar_operacao_unidades"], "Resgate", "Ninguém", None, 1000, "Ordinária", date.today(), "RES-2")


@teste
def resgate_valido_e_anulacao_com_estorno():
    preparar_base_validada()
    base = ns["obter_vup_info"]()
    ns["registar_operacao_unidades"]("Subscrição", "Novo", None, 500000, "Ordinária", date.today(), "S-1")
    mov_id = consultar_um("SELECT id FROM unidades_movimentos WHERE referencia = 'S-1'")[0]
    levanta(ValueError, ns["anular_movimento_unidades"], mov_id, "")                      # motivo obrigatório
    ns["anular_movimento_unidades"](mov_id, "Registado por engano (teste)")
    pos = ns["obter_vup_info"]()
    assert abs(pos["unidades"] - base["unidades"]) < 1e-6 and abs(pos["dinheiro"] - base["dinheiro"]) < 0.005   # estorno repõe unidades e caixa
    assert consultar_um("SELECT estado, motivo_anulacao, anulado_por FROM unidades_movimentos WHERE id = %s", (mov_id,)) == ("Anulado", "Registado por engano (teste)", "admin@teste.ao")
    levanta(ValueError, ns["anular_movimento_unidades"], mov_id, "outra vez")             # já anulado
    assert consultar_um("SELECT COUNT(*) FROM unidades_movimentos WHERE id = %s", (mov_id,))[0] == 1                  # nunca apaga
    ns["registar_operacao_unidades"]("Subscrição", "Novo2", None, 300000, "Ordinária", date.today(), "S-2")
    ns["registar_operacao_unidades"]("Resgate", "Novo2", None, 100000, "Ordinária", date.today(), "R-2")
    assert consultar_um("SELECT COUNT(*) FROM auditoria")[0] >= 6


@teste
def concorrencia_serializada():
    preparar_base_validada()
    resultados = []
    def tentar(ref, mont):
        try:
            ns["registar_operacao_unidades"]("Subscrição", f"P-{ref}", None, mont, "Ordinária", date.today(), ref); resultados.append("ok")
        except ValueError as e:
            resultados.append("erro")
    st_antes = dict(st.session_state)
    ts = [threading.Thread(target=tentar, args=("CONC-SAME", 100000)) for _ in range(2)] + \
         [threading.Thread(target=tentar, args=(f"CONC-{i}", 200000 + i)) for i in range(3)]
    [t.start() for t in ts]; [t.join() for t in ts]
    assert resultados.count("ok") == 4 and resultados.count("erro") == 1, resultados     # a mesma referência só passa uma vez
    caixa = consultar_um("SELECT dinheiro_disponivel FROM balanco_privado ORDER BY data_ref DESC, id DESC LIMIT 1")[0]
    movs = consultar_um("SELECT COALESCE(SUM(efeito_caixa),0) FROM unidades_movimentos WHERE estado='Validado' AND referencia LIKE 'CONC-%%'")[0]
    assert abs(caixa - (D("2014073.93") + movs)) < D("0.005"), (caixa, movs)


@teste
def legado_por_rever_nao_conta_ate_ser_validado():
    papel(admin=True)
    executar("INSERT INTO unidades_movimentos (data, socio, tipo, montante, vup, unidades) VALUES (CURRENT_DATE, 'Legado', 'Subscrição inicial', 497836, 1000, 497.8362)")
    ns["inicializar_bd"]()                       # a migração marca como 'Por rever' sem apagar
    est = consultar_um("SELECT estado, origem FROM unidades_movimentos WHERE socio = 'Legado'")
    assert est[0] == "Por rever", est
    ns["registar_balanco"](date.today(), 1000, 0, 0, "x", "y", "Validado")
    i = ns["obter_vup_info"]()
    assert i["estado"] == "Não calculado" and i["unidades_por_rever"] > 0           # nada de VUP com base por rever
    mid = consultar_um("SELECT id FROM unidades_movimentos WHERE socio = 'Legado'")[0]
    levanta(ValueError, ns["validar_movimento_unidades"], mid, "")
    ns["corrigir_movimento_unidades"](mid, date.today(), "Legado", 497836, 100000, "Fundadora")
    ns["validar_movimento_unidades"](mid, "Acordo de participação (teste)")
    assert consultar_um("SELECT estado FROM unidades_movimentos WHERE id = %s", (mid,))[0] == "Validado"
    levanta(ValueError, ns["corrigir_movimento_unidades"], mid, date.today(), "Legado", 1, 1, "Fundadora")   # validados não se editam


@teste
def rotulos_publicos_anonimizados():
    nomes = ["Aníbal Alexandre Pereira da Costa", "Fundador II", "Fundador III", "Fundador IV", "Fundador V"]
    r = ns["rotulos_publicos"](nomes)
    assert r[nomes[0]] == "Aníbal Alexandre Pereira da Costa — Administrador Executivo"
    assert [r[n] for n in nomes[1:]] == ["Sócio II", "Sócio III", "Sócio IV", "Sócio V"]


if __name__ == "__main__":
    for nome, res, msg in RESULTADOS:
        print(f"{res:7} {nome}" + (f"  -> {msg}" if msg else ""))
    falhas = [r for r in RESULTADOS if r[1] != "OK"]
    print(f"\n{len(RESULTADOS) - len(falhas)}/{len(RESULTADOS)} testes passaram")
    sys.exit(1 if falhas else 0)
