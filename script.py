from faker import Faker
import random
import pandas as pd
from datetime import datetime, timedelta

# Configurar Faker para localidade brasileira
fake = Faker("pt_BR")

# Probabilidades para classificação social
SOCIAL_CLASSES = {
    "A": 0.05,
    "B": 0.15,
    "C": 0.20,
    "D": 0.30,
    "E": 0.30
}

# Faixas de renda mensal por classe social (valores aproximados do Brasil)
SOCIAL_CLASS_INCOME = {
    "A": (20000, 50000),
    "B": (10000, 20000),
    "C": (5000, 10000),
    "D": (2000, 5000),
    "E": (0, 2000)
}

# Faixas de limite de crédito baseadas na classe social
SOCIAL_CLASS_CREDIT_LIMIT = {
    "A": (30000, 100000),
    "B": (15000, 30000),
    "C": (5000, 15000),
    "D": (1000, 5000),
    "E": (0, 1000)
}

# Taxas de inadimplência por classe social
SOCIAL_CLASS_DELINQUENCY_RATE = {
    "A": 0.01,
    "B": 0.02,
    "C": 0.05,
    "D": 0.10,
    "E": 0.15
}

# Função para definir classe social com base nas probabilidades
def get_social_class():
    return random.choices(
        population=list(SOCIAL_CLASSES.keys()),
        weights=list(SOCIAL_CLASSES.values()),
        k=1
    )[0]

# Função para gerar contas
def generate_account(account_id, social_class):
    credit_limit_range = SOCIAL_CLASS_CREDIT_LIMIT[social_class]
    credit_limit = round(random.uniform(*credit_limit_range), 2)
    return {
        "accountId": account_id,
        "brandName": fake.company(),
        "companyCnpj": fake.cnpj(),
        "name": fake.word().capitalize() + " Crédito",
        "productType": "CREDIT",
        "creditCardNetwork": random.choice(["VISA", "MASTERCARD", "ELO"]),
        "creditLimit": credit_limit,
        "usedLimit": round(random.uniform(0, credit_limit), 2)
    }

# Função para gerar qualificações
def generate_qualification(account_id, social_class):
    income_range = SOCIAL_CLASS_INCOME[social_class]
    return {
        "accountId": account_id,
        "updateDateTime": fake.iso8601(),
        "companyCnpj": fake.cnpj(),
        "occupationCode": fake.random_int(min=1000, max=9999),
        "incomeFrequency": "MENSAL",
        "incomeAmount": round(random.uniform(*income_range), 2)
    }

# Função para gerar relações financeiras
def generate_financial_relation(account_id):
    patrimony = round(random.uniform(1000, 500000), 2)
    annual_income = patrimony * random.uniform(0.05, 0.2)
    return {
        "accountId": account_id,
        "informedPatrimony": patrimony,
        "informedIncome": round(annual_income, 2),
        "frequency": "ANUAL"
    }

# Função para gerar faturas
def generate_bills(account_id, social_class):
    bills = []
    for i in range(12):  # 12 meses
        due_date = fake.date_this_year(before_today=False, after_today=True)
        total_amount = round(random.uniform(100, 5000), 2)
        # Determinar se a fatura será paga ou não
        is_paid = random.random() > SOCIAL_CLASS_DELINQUENCY_RATE[social_class]
        bills.append({
            "billId": fake.uuid4(),
            "accountId": account_id,
            "dueDate": due_date,
            "billTotalAmount": {
                "amount": total_amount,
                "currency": "BRL"
            },
            "billMinimumAmount": {
                "amount": round(total_amount * random.uniform(0.1, 0.5), 2),
                "currency": "BRL"
            },
            "isPaid": is_paid
        })
    return bills

# Função para gerar transações
def generate_transactions(account_id, bills):
    transactions = []
    for bill in bills:
        num_transactions = random.randint(3, 20)
        for _ in range(num_transactions):
            transaction_date = fake.date_between_dates(
                date_start=bill["dueDate"] - timedelta(days=30),
                date_end=bill["dueDate"]
            )
            transactions.append({
                "transactionId": fake.uuid4(),
                "accountId": account_id,
                "billId": bill["billId"],
                "transactionDate": transaction_date,
                "transactionalAmount": round(random.uniform(10, 1000), 2),
                "merchantName": fake.company(),
                "creditDebitType": "CREDITO",
                "transactionType": random.choice(["COMPRA", "JUROS"])
            })
    return transactions

# Função para gerar limites
def generate_limits(account_id, social_class):
    credit_limit_range = SOCIAL_CLASS_CREDIT_LIMIT[social_class]
    total_limit = round(random.uniform(*credit_limit_range), 2)
    used_limit = round(random.uniform(0, total_limit), 2)
    return {
        "accountId": account_id,
        "creditLineLimitType": "LIMITE_CREDITO_TOTAL",
        "limitAmount": {
            "amount": total_limit,
            "currency": "BRL"
        },
        "usedAmount": {
            "amount": used_limit,
            "currency": "BRL"
        },
        "availableAmount": {
            "amount": total_limit - used_limit,
            "currency": "BRL"
        }
    }

# Gerar dados
accounts_data = []
qualifications_data = []
financial_relations_data = []
bills_data = []
transactions_data = []
limits_data = []

# Criar 100 contas de crédito
for i in range(1, 101):
    account_id = fake.uuid4()
    social_class = get_social_class()
    
    account = generate_account(account_id, social_class)
    qualification = generate_qualification(account_id, social_class)
    financial_relation = generate_financial_relation(account_id)
    limits = generate_limits(account_id, social_class)

    accounts_data.append(account)
    qualifications_data.append(qualification)
    financial_relations_data.append(financial_relation)
    limits_data.append(limits)

    bills = generate_bills(account_id, social_class)
    bills_data.extend(bills)

    transactions = generate_transactions(account_id, bills)
    transactions_data.extend(transactions)

# Converter para DataFrames
accounts_df = pd.DataFrame(accounts_data)
qualifications_df = pd.DataFrame(qualifications_data)
financial_relations_df = pd.DataFrame(financial_relations_data)
bills_df = pd.DataFrame(bills_data)
transactions_df = pd.DataFrame(transactions_data)
limits_df = pd.DataFrame(limits_data)

# Salvar os DataFrames em arquivos CSV
accounts_df.to_csv("accounts.csv", index=False)
qualifications_df.to_csv("qualifications.csv", index=False)
financial_relations_df.to_csv("financial_relations.csv", index=False)
bills_df.to_csv("bills.csv", index=False)
transactions_df.to_csv("transactions.csv", index=False)
limits_df.to_csv("limits.csv", index=False)

print("Arquivos gerados: accounts.csv, qualifications.csv, financial_relations.csv, bills.csv, transactions.csv, limits.csv")
