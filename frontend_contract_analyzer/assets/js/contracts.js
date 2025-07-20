const apiBaseUrl = "http://localhost:8000";

// Seleciona os elementos
const fileInput = document.getElementById("filename");
const saveButton = document.getElementById("saveButton");

// Desativa o botão "Salvar" inicialmente
saveButton.disabled = true;


function logout() {
    // Remove o token
    localStorage.removeItem("accessToken");

    // Redireciona para tela de login
    window.location.href = "login.html";
}


// ------------ C O N T R A T O S  -  DELETE, VER DETALHES E LISTAR  ---------------------------------------------

async function deleteContract(id) {
    id = parseInt(id); // garante que o ID é número
    if (isNaN(id)) {
        alert("ID inválido para exclusão.");
        return;
    }

    if (confirm("Tem certeza que deseja excluir este contrato?")) {
        try {
            const token = localStorage.getItem("accessToken"); // pega o token salvo no login
            if (!token) {
                alert("Sessão expirada. Faça login novamente.");
                window.location.href = "login.html";
                return;
            }

            const res = await fetch(`${apiBaseUrl}/contracts/${id}`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}` // adiciona o token no cabeçalho
                }
            });

            if (res.ok) {
                alert("Contrato excluído com sucesso!");
                loadContracts(); // Atualiza a lista
            } else if (res.status === 401 || res.status === 403) {
                alert("Sessão expirada. Faça login novamente.");
                localStorage.removeItem("accessToken");
                window.location.href = "login.html";
            } else {
                alert("Erro ao excluir contrato.");
                console.error("Erro ao excluir:", await res.text());
            }
        } catch (error) {
            //console.error("Erro ao excluir contrato:", error);
            alert("Erro ao excluir contrato.");
        }
    }
}

async function viewDetails(id) {
    try {
        const token = localStorage.getItem("accessToken");
        const res = await fetch(`${apiBaseUrl}/contracts/${id}`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) {
            alert("Erro ao buscar detalhes do contrato.");
            return;
        }

        const contract = await res.json();

        // Preencher os campos do modal
        document.getElementById("detailId").textContent = contract.id;
        document.getElementById("detailFilename").textContent = contract.filename;
        document.getElementById("detailNomesPartes").textContent = contract.nomes_partes || "N/A";
        document.getElementById("detailValoresMonetarios").textContent = contract.valores_monetarios || "N/A";
        document.getElementById("detailObrigacoesPrincipais").textContent = contract.obrigacoes_principais || "N/A";
        document.getElementById("detailDadosAdicionais").textContent = contract.dados_adicionais || "N/A";
        document.getElementById("detailClausulasRescisao").textContent = contract.clausulas_rescisao || "N/A";

        // Abrir modal
        $('#detailsModal').modal('show');
    } catch (error) {
        //console.error("Erro ao carregar detalhes do contrato:", error);
        alert("Erro ao carregar detalhes do contrato.");
    }
}

// Listar Contratos
async function loadContracts() {

    try {
        const token = localStorage.getItem("accessToken");
        if (!token) {
            alert("Usuário não autenticado. Faça login novamente.");
            window.location.href = "login.html";
            return;
        }

        const res = await fetch(`${apiBaseUrl}/contracts`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        
        if (res.status === 401 || res.status === 403) {
            alert("Sessão expirada. Faça login novamente.");
            localStorage.removeItem("accessToken");
            window.location.href = "login.html";
            return;
        }

        if (res.status === 404) {
            alert("Você não possui nenhum contrato carregado!");
            return;
        }

        const data = await res.json();
        const contracts = data.contracts;
        const table = document.getElementById("contractsTable");
        table.innerHTML = "";


        contracts.forEach(contract => {
            const row = `
            <tr>
                <td>${contract.id}</td>
                <td title="${contract.filename}">${contract.filename}</td>
                <td title="${contract.nomes_partes}">${contract.nomes_partes || ""}</td>
                <td title="${contract.valores_monetarios}">${contract.valores_monetarios || ""}</td>
                <td title="${contract.obrigacoes_principais}">${contract.obrigacoes_principais || ""}</td>
                <td title="${contract.dados_adicionais}">${contract.dados_adicionais || ""}</td>
                <td title="${contract.clausulas_rescisao}">${contract.clausulas_rescisao || ""}</td>
                <td class="actions">
                    <button class="btn btn-sm btn-info" onclick="viewDetails(${contract.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="openEditModal(${contract.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteContract(${contract.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>`;
            table.innerHTML += row;
        });

    } catch (error) {
        //console.error("Erro ao carregar contratos:", error);
        alert("Erro ao carregar contratos.");
    }
}


// ------------ M O D A L  CONTRATOS   -   U P L O A D   ---------------------------------------------

// Habilita o botão quando o usuário carrega um arquivo
fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        saveButton.disabled = false;
    } else {
        saveButton.disabled = true;
    }
});

//U P L O A D 
async function uploadAndExtract() {
    const fileInput = document.getElementById("filename");
    const formData = new FormData();
    const saveButton = document.getElementById("saveButton");

    // Desativa o botão "Salvar" no início
    saveButton.disabled = true;

    if (fileInput.files.length === 0) {
        alert("Por favor, selecione um arquivo.");
        return;
    }

    formData.append("file", fileInput.files[0]);

    try {
        const token = localStorage.getItem("accessToken");
        const uploadRes = await fetch(`${apiBaseUrl}/contracts/upload`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: formData
        });

        if (uploadRes.status === 409) {
            // Arquivo duplicado
            alert("Já existe um contrato com este nome no sistema.");
            saveButton.disabled = true; // mantém desativado
            return;
        }

        if (uploadRes.status === 422) {
            // Erro na extração de dados
            alert("Erro ao extrair o texto do contrato. Verifique o formato do arquivo e tente novamente.");
            saveButton.disabled = true; // mantém desativado
            return;
        }
        
        if (uploadRes.status === 500) {
            // Erro ao processo o texto do contrato com a IA
            alert("Erro ao processar o contrato com a IA.");
            saveButton.disabled = true; // mantém desativado
            return;
        }

        if (uploadRes.status === 503) {
            // Erro na habilitação do serviço de IA (Gemini)
            alert("Serviço de IA (Gemini) não está habilitado. Configure a chave API para usar esta funcionalidade.");
            saveButton.disabled = true; // mantém desativado
            return;
        }

        if (!uploadRes.ok) {
            alert("Erro inesperado ao enviar o arquivo.");
            saveButton.disabled = true; // mantém desativado
            return;
        }

        const uploadData = await uploadRes.json();

        // Preenche os campos do modal com os dados extraídos
        document.getElementById("contractId").value = uploadData.id;
        document.getElementById("nomesPartes").value = (uploadData.analysis.nomes_partes || []).join("; ");
        document.getElementById("valoresMonetarios").value = (uploadData.analysis.valores_monetarios || []).join("; ");
        document.getElementById("obrigacoesPrincipais").value = (uploadData.analysis.obrigacoes_principais || []).join("\n");
        document.getElementById("dadosAdicionais").value = uploadData.analysis.dados_adicionais || "";
        document.getElementById("clausulasRescisao").value = uploadData.analysis.clausulas_rescisao || "";

        alert("Dados extraídos com sucesso! Revise e clique em Salvar para confirmar.");

        saveButton.disabled = false; // habilita somente após sucesso
    } catch (error) {
        console.error("Erro ao enviar o arquivo:", error);
        alert("Erro inesperado ao enviar o arquivo.");
        saveButton.disabled = true; // mantém desativado em erro inesperado
    }
}


// Mostra o campo de upload e oculta o campo somente leitura
function openCreateModal() {
    document.getElementById("contractForm").reset();
    document.getElementById("contractId").value = "";
    document.getElementById("contractModalLabel").textContent = "Novo Contrato";

    // Mostra o campo de upload e oculta o campo de exibição
    document.getElementById("fileUploadGroup").style.display = "block";
    document.getElementById("filenameDisplay").style.display = "none";

    $('#contractModal').modal('show');
}


// ------------ M O D A L  CONTRATOS   -   E D I Ç Ã O   ---------------------------------------------

document.getElementById("contractForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("contractId").value.trim();
    const token = localStorage.getItem("accessToken");

    if (!token) {
        alert("Sessão expirada. Faça login novamente.");
        window.location.href = "login.html";
        return;
    }

    if (!id) {
        alert("Por favor, carregue um arquivo antes de salvar.");
        return;
    }

    try {
        // Atualiza apenas os campos (sem upload)
        const updateData = {
            nomes_partes: document.getElementById("nomesPartes").value,
            valores_monetarios: document.getElementById("valoresMonetarios").value,
            obrigacoes_principais: document.getElementById("obrigacoesPrincipais").value,
            dados_adicionais: document.getElementById("dadosAdicionais").value,
            clausulas_rescisao: document.getElementById("clausulasRescisao").value
        };

        const updateRes = await fetch(`${apiBaseUrl}/contracts/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(updateData)
        });

        if (updateRes.ok) {
            $('#contractModal').modal('hide');
            loadContracts();
            alert("Contrato salvo com sucesso!");
        } else {
            alert("Erro ao salvar contrato.");
        }
    } catch (error) {
        console.error("Erro ao salvar contrato:", error);
        alert("Erro ao salvar contrato.");
    }
});


async function openEditModal(id) {
    const saveButton = document.getElementById("saveButton");
    const filenameDisplay = document.getElementById("filenameDisplay");

    saveButton.disabled = true; // Desativa enquanto carrega dados

    try {
        const token = localStorage.getItem("accessToken");
        if (!token) {
            alert("Sessão expirada. Faça login novamente.");
            window.location.href = "login.html";
            return;
        }

        const res = await fetch(`${apiBaseUrl}/contracts/${id}`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) {
            if (res.status === 401 || res.status === 403) {
                alert("Sessão expirada. Faça login novamente.");
                localStorage.removeItem("accessToken");
                window.location.href = "login.html";
            } else if (res.status === 404) {
                alert("Contrato não encontrado.");
            } else {
                alert("Erro ao carregar contrato.");
            }
            return;
        }

        const contract = await res.json();

        // Oculta o campo de upload
        document.getElementById("fileUploadGroup").style.display = "none";

        // Remove obrigatoriedade do campo ao submeter formulário
        fileInput.required = false;

        // Mostra o campo somente leitura com o nome do arquivo
        filenameDisplay.style.display = "block";
        filenameDisplay.value = contract.filename || "Arquivo não encontrado";

        // Preenche os outros campos
        document.getElementById("contractId").value = contract.id;
        document.getElementById("nomesPartes").value = contract.nomes_partes || "";
        document.getElementById("valoresMonetarios").value = contract.valores_monetarios || "";
        document.getElementById("obrigacoesPrincipais").value = contract.obrigacoes_principais || "";
        document.getElementById("dadosAdicionais").value = contract.dados_adicionais || "";
        document.getElementById("clausulasRescisao").value = contract.clausulas_rescisao || "";
        document.getElementById("contractModalLabel").textContent = "Editar Contrato";

        $('#contractModal').modal('show');
        saveButton.disabled = false; // Habilita o botão só após sucesso

    } catch (error) {
        console.error("Erro ao carregar contrato:", error);
        alert("Erro ao carregar contrato.");
    }
}


document.addEventListener("DOMContentLoaded", loadContracts);
