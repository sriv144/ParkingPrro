import { createRouter, createWebHistory } from "vue-router";

import LandingPage from "@/components/LandingPage.vue";
import LoginPage from "@/components/Login.vue";
import RegisterPage from "@/components/Register.vue";
import AdminLayout from "@/components/AdminDashboard.vue";
import LotList from "@/components/LotList.vue";
import AddLot from "@/components/AddLot.vue";
import EditLot from "@/components/EditLot.vue";
import OccupiedSpotDetails from "@/components/OccupiedSpotDetails.vue";
import UserList from "@/components/RegisteredUsers.vue";
import SearchParkingLots from "@/components/SearchParkingLots.vue";
import SummaryView from "@/components/SummaryView.vue";

const routes = [
  { path: "/",        name: "Home",      component: LandingPage },
  { path: "/login",   name: "Login",     component: LoginPage   },
  { path: "/register", name: "Register", component: RegisterPage },

  {
    path: "/admin",
    component: AdminLayout,
    children: [
      { path: "",           name: "AdminDashboard",     component: LotList },
      { path: "lots",       name: "ParkingLots",        component: LotList },
      { path: "add-lot",    name: "AddLot",             component: AddLot },
      { path: "edit-lot/:id", name: "EditLot",          component: EditLot, props: true },
      { path: "occupied-spot/:id", name: "OccupiedSpotDetails", component: OccupiedSpotDetails, props: true },
      { path: "users",      name: "Users",              component: UserList },
      { path: "search",     name: "SearchParkingLots",  component: SearchParkingLots },
      { path: "summary",    name: "Summary",            component: SummaryView },
    ]
  },

  { path: "/:pathMatch(.*)*", redirect: "/" }
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
