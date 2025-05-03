# Guia de Uso do Sistema ControleVendas

## Índice
1. [Instalação e Configuração Inicial](#instalação-e-configuração-inicial)
2. [Acesso ao Sistema](#acesso-ao-sistema)
3. [Gerenciamento de Produtos](#gerenciamento-de-produtos)
4. [Registro de Vendas](#registro-de-vendas)
5. [Controle de Clientes](#controle-de-clientes)
6. [Visualização de Relatórios](#visualização-de-relatórios)
7. [Gerenciamento de Usuários](#gerenciamento-de-usuários)
8. [Dicas Importantes](#dicas-importantes)
9. [Manutenção](#manutenção)
10. [Suporte](#suporte)

## Instalação e Configuração Inicial

1. Instale o Python em seu computador
2. Clone o repositório do projeto
3. Crie e ative um ambiente virtual
4. Instale as dependências usando `pip install -r requirements.txt`
5. Execute as migrações do banco de dados com `python manage.py migrate`
6. Crie um usuário administrador com `python manage.py createsuperuser`
7. Inicie o servidor com `python manage.py runserver`

## Acesso ao Sistema

- Abra seu navegador e acesse `http://127.0.0.1:8000/`
- Faça login com suas credenciais de administrador

## Gerenciamento de Produtos

- Acesse a seção de produtos
- Adicione novos produtos com:
  - Nome do produto
  - Preço
  - Quantidade em estoque
  - Unidade de medida
  - Descrição (opcional)
- Monitore o estoque e receba alertas quando estiver baixo

## Registro de Vendas

- Acesse a seção de vendas
- Selecione os produtos vendidos
- Registre a quantidade vendida
- Escolha o método de pagamento
- Para vendas a prazo, registre os dados do cliente
- O sistema atualizará automaticamente o estoque

## Controle de Clientes

- Cadastre clientes com:
  - Nome
  - Contato
  - Endereço (opcional)
- Acompanhe o histórico de compras
- Gerencie vendas a prazo

## Visualização de Relatórios

- Acesse os dashboards para:
  - Ver gráficos de vendas
  - Analisar produtos mais vendidos
  - Verificar movimentação de estoque
  - Acompanhar desempenho financeiro

## Gerenciamento de Usuários

- Como administrador, você pode:
  - Criar novos usuários
  - Definir níveis de acesso
  - Gerenciar permissões

## Dicas Importantes

- Sempre mantenha o estoque atualizado
- Registre todas as vendas imediatamente
- Verifique regularmente os relatórios para tomar decisões estratégicas
- Use os alertas de estoque para evitar rupturas

## Manutenção

- Faça backup regular do banco de dados
- Mantenha o sistema atualizado
- Reporte problemas ou sugestões de melhorias

## Suporte

Em caso de dúvidas, entre em contato:
- Email: ifraiaraujo@gmail.com
- Instagram: rai.limaarj

---

**Observação:** O sistema foi projetado para ser intuitivo e fácil de usar, com uma interface amigável que permite o gerenciamento eficiente do seu negócio. Lembre-se de sempre manter os dados atualizados para garantir a precisão dos relatórios e análises. 