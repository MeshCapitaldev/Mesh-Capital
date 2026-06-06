import { createRouter, createWebHistory } from "vue-router";
import Route from "@/views/Route.vue";
import Perps from "@/views/Perps.vue";
import Vaults from "@/views/Vaults.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "Route", component: Route },
    { path: "/perps", name: "Perps", component: Perps },
    { path: "/vaults", name: "Vaults", component: Vaults },
  ],
});
