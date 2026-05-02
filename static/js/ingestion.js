document.addEventListener("DOMContentLoaded", function() {

    const fournisseurSelect = document.getElementById("fournisseur");
    const sourceSelect = document.getElementById("source_id");
    const formIngestion = document.getElementById("form-ingestion");
    const messageDiv = document.getElementById("message");

    // Lorsque le fournisseur change, charger les sources correspondantes
    fournisseurSelect.addEventListener("change", function() {
        const fournisseur = this.value;
        if (!fournisseur) {
            formIngestion.style.display = "none";
            sourceSelect.innerHTML = "";
            return;
        }

        fetch(`/api/get-sources/${encodeURIComponent(fournisseur)}`)
            .then(response => response.json())
            .then(data => {
                sourceSelect.innerHTML = "";
                if (data.sources.length > 0) {
                    data.sources.forEach(src => {
                        const option = document.createElement("option");
                        option.value = src.id;
                        option.textContent = src.intitule_source;
                        sourceSelect.appendChild(option);
                    });
                    formIngestion.style.display = "block";
                } else {
                    sourceSelect.innerHTML = "<option value=''>Aucune source disponible</option>";
                    formIngestion.style.display = "none";
                }
            })
            .catch(err => {
                console.error(err);
                messageDiv.textContent = "Erreur lors du chargement des sources.";
            });
    });

    // Gestion de l'upload du fichier
    formIngestion.addEventListener("submit", function(e) {
        e.preventDefault();
        messageDiv.textContent = "";

        const formData = new FormData(formIngestion);
        formData.append("fournisseur", fournisseurSelect.value);

        fetch("/api/upload", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                messageDiv.style.color = "green";
                messageDiv.textContent = data.message;
                setTimeout(() => location.reload(), 1000); // rafraîchit la page pour afficher l'historique
            } else {
                messageDiv.style.color = "red";
                messageDiv.textContent = data.message;
            }
        })
        .catch(err => {
            console.error(err);
            messageDiv.style.color = "red";
            messageDiv.textContent = "Erreur lors de l'upload du fichier.";
        });
    });

});
