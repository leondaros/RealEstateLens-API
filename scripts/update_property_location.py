from real_estate_lens.models  import Property, Location

# Obtém Garopaba
try:
    garopaba = Location.objects.get(name="Garopaba")
except Location.DoesNotExist:
    raise ValueError("Localização Garopaba não encontrada.")

# Obtém todas as sublocalizações de Garopaba
sublocations = Location.objects.filter(parent=garopaba)

if not sublocations.exists():
    raise ValueError("Nenhuma sublocalização encontrada para Garopaba.")

# Itera sobre todas as propriedades e compara com as sublocalizações
properties = Property.objects.all()

for property in properties:
    for sublocation in sublocations:
        try:
            # Tenta atualizar a propriedade se ela estiver dentro da sublocalização
            updated = property.update_location(sublocation.id)
            if updated:
                print(f"Propriedade {property.id} atualizada com a sublocalização {sublocation.name}.")
                break  # Sai do loop para evitar múltiplas atualizações
        except ValueError as e:
            print(f"Erro ao processar propriedade {property.id}: {e}")
