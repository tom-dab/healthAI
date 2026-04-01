import { useEffect, useState } from "react";
import { exercisesAPI } from "../services/api";
import Table from "../components/Table";
import Loader from "../components/Loader";
import Card from "../components/Card";

export default function Exercises() {
  const [exercises, setExercises] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    type: "",
    muscle_group: "",
    difficulty: "",
    search: ""
  });

  useEffect(() => {
    loadExercises();
  }, [filters]);

  const loadExercises = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.type) params.type = filters.type;
      if (filters.muscle_group) params.muscle_group = filters.muscle_group;
      if (filters.difficulty) params.difficulty = filters.difficulty;
      if (filters.search) params.search = filters.search;

      const response = await exercisesAPI.getExercises(params);
      setExercises(response.data);
    } catch (error) {
      console.error("Erreur chargement exercices:", error);
      setExercises([]);
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
        <h1 className="text-3xl font-bold text-gray-900">Exercices</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          Ajouter un exercice
        </button>
      </div>

      {/* Filtres */}
      <Card>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={filters.type}
              onChange={(e) => handleFilterChange("type", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Tous</option>
              <option value="cardio">Cardio</option>
              <option value="strength">Force</option>
              <option value="flexibility">Flexibilité</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Groupe musculaire
            </label>
            <select
              value={filters.muscle_group}
              onChange={(e) => handleFilterChange("muscle_group", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Tous</option>
              <option value="chest">Pectoraux</option>
              <option value="back">Dos</option>
              <option value="legs">Jambes</option>
              <option value="arms">Bras</option>
              <option value="shoulders">Épaules</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Difficulté
            </label>
            <select
              value={filters.difficulty}
              onChange={(e) => handleFilterChange("difficulty", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Toutes</option>
              <option value="beginner">Débutant</option>
              <option value="intermediate">Intermédiaire</option>
              <option value="advanced">Avancé</option>
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
              placeholder="Nom de l'exercice..."
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
        </div>
      </Card>

      {/* Liste des exercices */}
      <Card>
        {exercises && exercises.length > 0 ? (
          <Table data={exercises} />
        ) : (
          <div className="text-center py-8 text-gray-500">
            Aucun exercice trouvé
          </div>
        )}
      </Card>
    </div>
  );
}