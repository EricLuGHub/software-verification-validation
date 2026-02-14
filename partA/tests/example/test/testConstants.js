const host = "http://localhost:4567";
const todosEndpoint = "/todos";
const projectsEndpoint = "/projects";
const categsEndpoint = "/categories";
const projTodoRelationship = "tasks";
const todoProjRelationship = "tasksof";
const categoriesRelationship = "categories";
const categProjRelationship = "projects";
const categTodosRelationship = "todos";

module.exports = {
  host: host,
  todosEndpoint: todosEndpoint,
  projectsEndpoint: projectsEndpoint,
  categsEndpoint: categsEndpoint,
  projTodoRelationship: projTodoRelationship,
  todoProjRelationship: todoProjRelationship,
  categoriesRelationship: categoriesRelationship,
  categProjRelationship: categProjRelationship,
  categTodosRelationship: categTodosRelationship,
};
