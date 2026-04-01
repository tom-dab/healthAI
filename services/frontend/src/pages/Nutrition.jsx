import { useEffect, useState } from "react";
import { nutritionAPI } from "../services/api";
import Table from "../components/Table";
import Loader from "../components/Loader";
import Card from "../components/Card";

export default function Nutrition() {
  const [nutritionItems, setNutritionItems] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: "",
    search: ""
  });

  useEffect(() => {
    loadNutritionItems();
  }, [filters]);

  const loadNutritionItems = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.category) params.category = filters.category;
      if (filters.search) params.search = filters.search;

      const response = await nutritionAPI.getNutritionItems(params);
      setNutritionItems(response.data);
    } catch (error) {
      console.error("Erreur chargement aliments:", error);
      setNutritionItems([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  if (loading) return <Loader />;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Nutrition</h1>
        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
          Ajouter un aliment
        </button>
      </div>

      {/* Filtres */}
      <Card>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Catégorie
            </label>
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange("category", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Toutes</option>
              <option value="fruits">Fruits</option>
              <option value="vegetables">Légumes</option>
              <option value="proteins">Protéines</option>
              <option value="grains">Céréales</option>
              <option value="dairy">Produits laitiers</option>
              <option value="fats">Matières grasses</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recherche
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => handleFilterChange("search", e.target.value)}
              placeholder="Nom de l'aliment..."
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
        </div>
      </Card>

      {/* Liste des aliments */}
      <Card>
        {nutritionItems && nutritionItems.length > 0 ? (
          <Table data={nutritionItems} />
        ) : (
          <div className="text-center py-8 text-gray-500">
            Aucun aliment trouvé
          </div>
        )}
      </Card>
    </div>
  );
}