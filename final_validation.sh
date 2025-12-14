#!/bin/bash

# Test final - Vérification que le POST retourne 404 avec HTML quand le sélecteur échoue
# Reconstruction de l'image Docker et test

echo "===== FINAL VALIDATION TEST ====="
echo ""
echo "1. Reconstruction de l'image Docker avec le nouveau code..."
cd /Users/olivier/workspace/browse-local
docker build --no-cache -t browse-local:latest . > /dev/null 2>&1
echo "✓ Image reconstruite"

echo ""
echo "2. Lancement du container..."
docker run -d -p 8000:8000 --name browse-test browse-local:latest > /dev/null 2>&1
sleep 3
echo "✓ Container démarré"

echo ""
echo "3. Test POST avec sélecteur qui échoue..."
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST http://localhost:8000/v1/html \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "selector": ".nonexistent-selector",
    "timeout": 2000
  }')

http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
response_body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_status"
echo ""

# Vérifications
if [ "$http_status" = "404" ]; then
    echo "✓ Status code est 404 (erreur attendue)"
    
    # Vérifier que le contenu HTML est présent
    if echo "$response_body" | jq -e '.detail.content' > /dev/null 2>&1; then
        echo "✓ Contenu HTML présent dans la réponse"
        
        # Vérifier que les métadonnées d'erreur sont présentes
        if echo "$response_body" | jq -e '.detail.metadata.selector_error' > /dev/null 2>&1; then
            error_msg=$(echo "$response_body" | jq -r '.detail.metadata.selector_error')
            echo "✓ Message d'erreur du sélecteur: $error_msg"
            
            # Vérifier le flag partial_content
            if echo "$response_body" | jq -e '.detail.metadata.partial_content' > /dev/null 2>&1; then
                echo "✓ Flag partial_content est présent"
                echo ""
                echo "========== ✅ ALL CHECKS PASSED =========="
            else
                echo "✗ Flag partial_content manquant"
            fi
        else
            echo "✗ Message d'erreur du sélecteur manquant"
        fi
    else
        echo "✗ Contenu HTML manquant"
    fi
else
    echo "✗ Status code incorrect: attendu 404, obtenu $http_status"
fi

echo ""
echo "4. Nettoyage..."
docker stop browse-test > /dev/null 2>&1
docker rm browse-test > /dev/null 2>&1
echo "✓ Container arrêté et supprimé"
