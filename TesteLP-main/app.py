from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import date, datetime
import firebase_admin
from firebase_admin import credentials, db
import csv
import io
import os
from calendar import monthrange
import json

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_aqui_2026"

# Inicializar Firebase
firebase_initialized = False

# Tentar ler credenciais do ambiente (Vercel)
firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
if firebase_creds_json:
    try:
        creds_dict = json.loads(firebase_creds_json)
        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://testelp-8517f-default-rtdb.europe-west1.firebasedatabase.app/'
        })
        firebase_initialized = True
        print("Firebase inicializado com credenciais do ambiente")
    except Exception as e:
        print(f"Erro ao inicializar Firebase com variável de ambiente: {e}")
else:
    # Tentar ler do ficheiro local (para desenvolvimento)
    firebase_config_path = "firebase-credentials.json"
    if os.path.exists(firebase_config_path):
        try:
            cred = credentials.Certificate(firebase_config_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://testelp-8517f-default-rtdb.europe-west1.firebasedatabase.app/'
            })
            firebase_initialized = True
            print("Firebase inicializado com ficheiro local")
        except Exception as e:
            print(f"Erro ao inicializar Firebase: {e}")
    else:
        print("Aviso: firebase-credentials.json não encontrado e FIREBASE_CREDENTIALS_JSON não está definido.")

# Fallback para armazenamento local se Firebase não estiver disponível
LOCAL_STORAGE_FILE = "votos_locais.json"

def salvar_voto_local(voto):
    """Salvar voto no arquivo local JSON"""
    try:
        votos = carregar_votos_locais()
        votos.append(voto)
        with open(LOCAL_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(votos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar voto local: {e}")
        return False

def carregar_votos_locais():
    """Carregar votos do arquivo local JSON"""
    try:
        if os.path.exists(LOCAL_STORAGE_FILE):
            with open(LOCAL_STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Erro ao carregar votos locais: {e}")
        return []

ADMIN_URL = "/admin_login"

# Dicionário de dias da semana em português
DIAS_SEMANA = {
    0: "Segunda",
    1: "Terça",
    2: "Quarta",
    3: "Quinta",
    4: "Sexta",
    5: "Sábado",
    6: "Domingo"
}

def get_dia_semana(data_str):
    """Obter nome do dia da semana"""
    data_obj = datetime.strptime(data_str, "%Y-%m-%d")
    return DIAS_SEMANA[data_obj.weekday()]

@app.route("/")
def index():
    """Página inicial para votação de satisfação"""
    return render_template("Index.html")

@app.route("/votar", methods=["POST"])
def votar():
    """Registar um voto de satisfação"""
    try:
        data = request.get_json()
        grau = data.get("grau")
        
        if grau not in ["Muito satisfeito", "Satisfeito", "Insatisfeito"]:
            return jsonify({"erro": "Grau inválido"}), 400
        
        hoje = date.today().strftime("%Y-%m-%d")
        dia_semana = get_dia_semana(hoje)
        agora = datetime.now().strftime("%H:%M:%S")
        timestamp = datetime.now().isoformat()
        
        # Registar o voto
        voto = {
            "grau": grau,
            "data": hoje,
            "dia_semana": dia_semana,
            "hora": agora,
            "criado_em": timestamp
        }
        
        if firebase_initialized:
            # Salvar no Firebase
            ref = db.reference("votos")
            ref.push(voto)
        else:
            # Salvar localmente
            if not salvar_voto_local(voto):
                return jsonify({"erro": "Erro ao salvar voto"}), 500
        
        return jsonify({"sucesso": True, "mensagem": "Voto registado com sucesso! Obrigado."})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/admin_login", methods=["GET", "POST"])
def login_admin():
    """Login para administrador"""
    if request.method == "POST":
        senha = request.form.get("senha")
        # ATENÇÃO: Usar variável de ambiente em produção!
        if senha == "admin1711":
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("admin_login.html", erro="Senha incorreta")
    
    return render_template("admin_login.html")

@app.route("/admin_login/logout")
def logout_admin():
    """Fazer logout do admin"""
    session.clear()
    return redirect(url_for("index"))

@app.route("/admin_login/dashboard")
def dashboard():
    """Dashboard com estatísticas"""
    if not session.get("admin"):
        return redirect(url_for("login_admin"))
    
    try:
        # Data selecionada (padrão: hoje)
        data_selecionada = request.args.get("data", date.today().strftime("%Y-%m-%d"))
        dia_semana_sel = get_dia_semana(data_selecionada)
        
        # Obter todos os votos
        if firebase_initialized:
            ref = db.reference("votos")
            votos_raw = ref.get()
            if not votos_raw:
                votos_raw = {}
            # Converter para lista com ids
            votos_list = []
            for key, voto in votos_raw.items():
                voto_copy = voto.copy()
                voto_copy['id'] = key
                votos_list.append(voto_copy)
        else:
            votos_list = carregar_votos_locais()
            votos_raw = {str(i): v for i, v in enumerate(votos_list)}
        
        # Filtrar votos do dia selecionado
        votos_dia = []
        for voto in votos_list:
            if voto.get("data") == data_selecionada:
                votos_dia.append(voto)
        
        # Estatísticas do dia
        stats = {}
        for voto in votos_dia:
            grau = voto.get("grau")
            stats[grau] = stats.get(grau, 0) + 1
        
        stats_list = [[grau, count] for grau, count in stats.items()]
        
        # Percentagens
        total_dia = len(votos_dia)
        percentagens = {}
        if total_dia > 0:
            for grau in ["Muito satisfeito", "Satisfeito", "Insatisfeito"]:
                count = stats.get(grau, 0)
                percentagens[grau] = round((count / total_dia) * 100, 1)
        
        # Paginação
        pagina = request.args.get("pagina", 1, type=int)
        registos_por_pagina = 20
        offset = (pagina - 1) * registos_por_pagina
        
        historico = sorted(votos_dia, key=lambda x: x.get("hora", ""), reverse=True)
        historico = historico[offset:offset + registos_por_pagina]
        
        total_paginas = (total_dia + registos_por_pagina - 1) // registos_por_pagina
        
        # Evolução últimos 7 dias
        evolucao_dict = {}
        for voto in votos_list:
            data_voto = voto.get("data")
            if data_voto:
                evolucao_dict[data_voto] = evolucao_dict.get(data_voto, 0) + 1
        
        # Ordenar últimos 7 dias
        from datetime import timedelta
        evolucao = []
        for i in range(7, -1, -1):
            data_check = (datetime.strptime(data_selecionada, "%Y-%m-%d") - timedelta(days=i)).strftime("%Y-%m-%d")
            evolucao.append([data_check, evolucao_dict.get(data_check, 0)])
        
        # Estatísticas globais
        stats_globais = {}
        for voto in votos_list:
            grau = voto.get("grau")
            stats_globais[grau] = stats_globais.get(grau, 0) + 1
        
        total_global = len(votos_list)
        percentagens_globais = {}
        if total_global > 0:
            for grau in ["Muito satisfeito", "Satisfeito", "Insatisfeito"]:
                count = stats_globais.get(grau, 0)
                percentagens_globais[grau] = round((count / total_global) * 100, 1)
        
        return render_template(
            "admin__dashboard.html",
            stats=stats_list,
            percentagens=percentagens,
            total_dia=total_dia,
            historico=historico,
            evolucao=evolucao,
            data_selecionada=data_selecionada,
            dia_semana_sel=dia_semana_sel,
            pagina=pagina,
            total_paginas=total_paginas,
            stats_globais=stats_globais,
            percentagens_globais=percentagens_globais,
            total_global=total_global
        )
    except Exception as e:
        return render_template("admin__dashboard.html", erro=f"Erro ao carregar dados: {str(e)}")

@app.route("/admin_login/export/csv")
def export_csv():
    """Exportar dados em CSV com formatação melhorada"""
    if not session.get("admin"):
        return redirect(url_for("login_admin"))
    
    try:
        data_filtro = request.args.get("data", None)
        
        # Obter todos os votos
        if firebase_initialized:
            ref = db.reference("votos")
            votos_raw = ref.get()
            if not votos_raw:
                votos_raw = {}
            votos_list = []
            for key, voto in votos_raw.items():
                voto_copy = voto.copy()
                voto_copy['id'] = key
                votos_list.append(voto_copy)
        else:
            votos_list = carregar_votos_locais()
        
        # Filtrar por data se especificada
        rows = []
        for voto in votos_list:
            if data_filtro is None or voto.get("data") == data_filtro:
                rows.append({
                    'id': voto.get('id', 'local'),
                    'grau': voto.get("grau", ""),
                    'data': voto.get("data", ""),
                    'dia_semana': voto.get("dia_semana", ""),
                    'hora': voto.get("hora", "")
                })
        
        # Ordenar por data e hora (mais recentes primeiro)
        rows = sorted(rows, key=lambda x: (x['data'], x['hora']), reverse=True)
        
        # Calcular estatísticas
        stats = {}
        for row in rows:
            grau = row['grau']
            stats[grau] = stats.get(grau, 0) + 1
        
        total = len(rows)
        
        # Criar CSV em memória com formatação melhorada
        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')
        
        # Cabeçalho informativo
        writer.writerow(["RELATÓRIO DE EXPORTAÇÃO - SATISFAÇÃO DOS CLIENTES"])
        writer.writerow([])
        writer.writerow([f"Data de Exportação: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"])
        if data_filtro:
            writer.writerow([f"Filtrado por Data: {data_filtro}"])
        else:
            writer.writerow(["Período: Completo"])
        writer.writerow([])
        
        # Separador
        writer.writerow(["="*80])
        writer.writerow([])
        
        # Tabela com title em português melhorado
        writer.writerow(["#", "ID do Registo", "Grau de Satisfação", "Data", "Dia da Semana", "Hora"])
        writer.writerow(["-"*80])
        
        # Dados com número de sequência
        for idx, row in enumerate(rows, 1):
            writer.writerow([
                idx,
                row['id'],
                row['grau'],
                row['data'],
                row['dia_semana'],
                row['hora']
            ])
        
        writer.writerow([])
        writer.writerow(["="*80])
        writer.writerow([])
        
        # Resumo estatístico
        writer.writerow(["RESUMO ESTATÍSTICO"])
        writer.writerow(["-"*80])
        writer.writerow(["Grau de Satisfação", "Quantidade", "Percentagem"])
        
        if total > 0:
            for grau in ["Muito satisfeito", "Satisfeito", "Insatisfeito"]:
                count = stats.get(grau, 0)
                percentage = (count / total) * 100
                writer.writerow([grau, count, f"{percentage:.1f}%"])
        
        writer.writerow([])
        writer.writerow(["Total de Registos", total, "100.0%"])
        writer.writerow([])
        writer.writerow(["="*80])
        
        # Preparar resposta
        output.seek(0)
        nome_ficheiro = f"satisfacao_{data_filtro or 'completo'}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.csv"
        return output.getvalue(), 200, {
            'Content-Disposition': f'attachment; filename={nome_ficheiro}',
            'Content-type': 'text/csv; charset=utf-8'
        }
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/admin_login/export/txt")
def export_txt():
    """Exportar dados em TXT com formatação melhorada"""
    if not session.get("admin"):
        return redirect(url_for("login_admin"))
    
    try:
        data_filtro = request.args.get("data", None)
        
        # Obter todos os votos
        if firebase_initialized:
            ref = db.reference("votos")
            votos_raw = ref.get()
            if not votos_raw:
                votos_raw = {}
            votos_list = []
            for key, voto in votos_raw.items():
                voto_copy = voto.copy()
                voto_copy['id'] = key
                votos_list.append(voto_copy)
        else:
            votos_list = carregar_votos_locais()
        
        # Filtrar por data se especificada
        rows = []
        for voto in votos_list:
            if data_filtro is None or voto.get("data") == data_filtro:
                rows.append({
                    'id': voto.get('id', 'local'),
                    'grau': voto.get("grau", ""),
                    'data': voto.get("data", ""),
                    'dia_semana': voto.get("dia_semana", ""),
                    'hora': voto.get("hora", "")
                })
        
        # Ordenar por data e hora (mais recentes primeiro)
        rows = sorted(rows, key=lambda x: (x['data'], x['hora']), reverse=True)
        
        # Calcular estatísticas
        stats = {}
        for row in rows:
            grau = row['grau']
            stats[grau] = stats.get(grau, 0) + 1
        
        total = len(rows)
        
        # Criar TXT formatado com melhor organização
        output = ""
        output += "╔" + "═" * 98 + "╗\n"
        output += "║" + " " * 25 + "RELATÓRIO DE SATISFAÇÃO DOS CLIENTES" + " " * 37 + "║\n"
        output += "╚" + "═" * 98 + "╝\n\n"
        
        output += f"Data de Exportação: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n"
        if data_filtro:
            output += f"Filtrado por Data: {data_filtro}\n"
        else:
            output += "Período: Completo\n"
        output += "\n"
        
        output += "─" * 100 + "\n"
        output += "REGISTOS DETALHADOS\n"
        output += "─" * 100 + "\n\n"
        
        # Cabeçalho da tabela com formatação melhorada
        output += f"{'#':<4} | {'ID do Registo':<20} | {'Grau de Satisfação':<20} | {'Data':<12} | {'Dia':<10} | {'Hora':<8}\n"
        output += "─" * 100 + "\n"
        
        # Dados com número de sequência
        for idx, row in enumerate(rows, 1):
            dia_formatado = row['dia_semana'][:3] if row['dia_semana'] else "N/A"
            output += f"{idx:<4} | {row['id']:<20} | {row['grau']:<20} | {row['data']:<12} | {dia_formatado:<10} | {row['hora']:<8}\n"
        
        output += "\n" + "─" * 100 + "\n"
        output += "RESUMO ESTATÍSTICO\n"
        output += "─" * 100 + "\n\n"
        
        output += f"{'Grau de Satisfação':<25} | {'Quantidade':<12} | {'Percentagem':<12}\n"
        output += "─" * 50 + "\n"
        
        if total > 0:
            for grau in ["Muito satisfeito", "Satisfeito", "Insatisfeito"]:
                count = stats.get(grau, 0)
                percentage = (count / total) * 100
                output += f"{grau:<25} | {count:<12} | {percentage:>10.1f}%\n"
        
        output += "─" * 50 + "\n"
        output += f"{'TOTAL':<25} | {total:<12} | {'100.0%':>10}\n"
        output += "\n" + "═" * 100 + "\n"
        
        nome_ficheiro = f"satisfacao_{data_filtro or 'completo'}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.txt"
        return output, 200, {
            'Content-Disposition': f'attachment; filename={nome_ficheiro}',
            'Content-type': 'text/plain; charset=utf-8'
        }
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
