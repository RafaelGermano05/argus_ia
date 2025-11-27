# 🛡️ ARGUS IA - Sistema de Detecção de Comportamentos Suspeitos

ARGUS IA é um sistema acadêmico desenvolvido para identificação de padrões suspeitos em redes sociais com foco na proteção de menores. O sistema integra geração de datasets simulados, análise por Machine Learning, exportação de relatórios e um dashboard web para visualização e acompanhamento das detecções.

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![Chart.js](https://img.shields.io/badge/chart.js-F5788D.svg?style=for-the-badge&logo=chart.js&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)


## Objetivos do Projeto

#### **Principal:** 

Desenvolver um serviço web que identifica perfis e postagens com comportamento suspeito visando a proteção de menores.

#### **Secundários:**

- Permitir geração de datasets simulados para testes;
- Prover análises automatizadas usando modelos clássicos de ML;
- Exportar relatórios em CSV/Excel;
- Disponibilizar um dashboard interativo para visualização das métricas e dos casos mais suspeitos.

## Motivação e Relevância Acadêmica

- **Problema social:** invisibilidade de comportamentos predatórios em plataformas sociais e a necessidade de ferramentas que auxiliem na triagem automática.

- **Contribuição acadêmica:** combinação de engenharia de software, ciência de dados e estudo de métricas de detecção (precisão, recall, F1), com possibilidade de extensões para modelos avançados (NLP, deep learning).

## Tecnologias e Dependências

- Backend: Django 4.2.
- ML / Data Science: Scikit-learn, Pandas, NumPy.
- Frontend: Bootstrap 5, Chart.js.
- Banco de Dados (dev): SQLite.

## Instalação e Execução (guia passo-a-passo)

### Requisitos

- Python 3.10+ (ou versão compatível com Django 4.2)
- pip
- virtualenv (recomendado)

### Passos

(1) Clone o repositório:

```bash
git clone https://github.com/RafaelGermano05/argus_ia.git
cd argus_ia
```

(2) Crie e ative ambiente virtual:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

(3) Instale dependências:

```bash
pip install -r requirements.txt
```

(4) Migrar banco:

```bash
python manage.py migrate
```

(5) (Opcional) Criar superuser:

```bash
python manage.py createsuperuser
```

(6) Executar servidor de desenvolvimento:

```bash
python manage.py runserver
```

(7) Acesse http://127.0.0.1:8000/ e navegue até o dashboard/detection.

> Observação: o repositório contém db.sqlite3, portanto pode haver dados de exemplo já disponíveis.

## Boas Práticas Recomendadas ao Reutilizar / Estender

- Separar ambiente de produção do de desenvolvimento: trocar SQLite por PostgreSQL em produção.
- Gerenciar segredos: variáveis sensíveis não devem estar no repositório.
- Testes automatizados: adicionar testes unitários e de integração (Django TestCase + pytest).
- Documentação de API: criar endpoints documentados (DRF + Swagger/OpenAPI se expandir API).
- Privacidade: garantir anonimização de dados de usuários reais.

## Limitações Conhecidas

- Uso de datasets simulados pode não refletir linguagem real de atacantes.
- Modelos de ML clássicos têm limitações para entender contexto e ironia, técnicas de NLP modernas (transformers) podem melhorar, mas exigem mais dados e processamento.
- Dependência de features manuais pode gerar falsos positivos por palavras fora de contexto.

## Licença e Créditos

MIT

---

> Este README foi preparado para servir como documentação inicial acadêmica do projeto ARGUS IA.

