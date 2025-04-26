# **Sistema de Gerenciamento de Vendas e Estoque**

O **ControleVendas** é um sistema desenvolvido para facilitar a gestão comercial, proporcionando um controle eficiente de vendas e estoque. Criado utilizando **Python** e **Django**, o projeto oferece uma interface intuitiva e **dashboards visuais** para uma análise estratégica dos negócios.

## **Objetivo do Projeto**

O **ControleVendas** foi projetado para otimizar a administração de comércios, proporcionando recursos para:

- **Registro eficiente de vendas** e acompanhamento de transações.
- **Monitoramento do estoque em tempo real** para evitar rupturas de produtos.
- **Visualização analítica do desempenho comercial** por meio de dashboards interativos.
- **Tomada de decisão baseada em dados**, garantindo maior previsibilidade e controle financeiro.

## **Principais Funcionalidades**

### **Gerenciamento de Produtos**
- Cadastro e edição de produtos com atualização dinâmica de preços e informações.
- Controle de estoque detalhado, permitindo acompanhamento de movimentações.
- Suporte a múltiplas unidades de medida.

### **Controle de Estoque**
- Alertas automáticos para níveis críticos de estoque.
- Histórico detalhado de movimentações para rastreamento de produtos.

### **Registro de Vendas**
- Registro de vendas individuais e por cliente, incluindo transações a prazo.
- Gestão de pagamentos e acompanhamento do histórico financeiro dos clientes.
- Emissão automática de recibos e faturas.

### **Dashboards e Relatórios**
- Visualização gráfica do desempenho das vendas.
- Identificação de produtos mais vendidos e comportamento do consumidor.

### **Gerenciamento de Usuários e Acesso**
- Controle de permissões e níveis de acesso por usuário.
- Administração de múltiplos estabelecimentos dentro do mesmo sistema.
- Segurança avançada para proteção de dados.

---

## **Tecnologias Utilizadas**

O sistema foi desenvolvido utilizando um conjunto de tecnologias modernas, garantindo escalabilidade e desempenho:

- **Backend:** Python (Django)
- **Banco de Dados:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Bibliotecas Adicionais:** Django Crispy Forms, Pillow, Django Filter

Essas tecnologias garantem um desenvolvimento ágil e uma interface responsiva.

---

## **Instalação e Configuração**

Para instalar e executar o sistema, siga os passos abaixo:

1. Clone o repositório:
   ```bash
   git clone https://github.com/RaiLimaa04/ControleVendas.git
   ```

2. Acesse o diretório do projeto:
   ```bash
   cd ControleVendas
   ```

3. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```

4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

5. Execute as migrações do banco de dados:
   ```bash
   python manage.py migrate
   ```

6. (Opcional) Crie um superusuário para acesso administrativo:
   ```bash
   python manage.py createsuperuser
   ```

7. Inicie o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

Acesse o sistema via navegador em [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/).

---

## **Contribuição**

Contribuições são bem-vindas. Para contribuir:

1. Realize um **fork** do repositório.
2. Crie uma **branch** para sua modificação:
   ```bash
   git checkout -b feature/sua-funcionalidade
   ```
3. Faça as alterações necessárias e adicione testes.
4. Envie suas alterações para o seu **fork**:
   ```bash
   git push origin feature/sua-funcionalidade
   ```
5. Abra um **pull request** para o repositório principal.

Sugestões para aprimorar o sistema, especialmente no uso de **inteligência artificial**, são altamente apreciadas.

---

## **Licença**

Este projeto **não possui uma licença específica**.

---

## **Contato**

Para dúvidas ou sugestões:

- **Email:** [ifraiaraujo@gmail.com](mailto:ifraiaraujo@gmail.com)
- **Instagram:** [rai.limaarj](https://www.instagram.com/rai.limaarj/)
