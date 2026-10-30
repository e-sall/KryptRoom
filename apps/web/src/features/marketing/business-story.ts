/** Fixed UI-only story. Not derived from cryptographic outputs or customer records. */
export const businessScenes = [
 {name:"Two Organizations",heading:"Two companies. One shared challenge.",description:"Understand supply chain risk without pooling sensitive records."},
 {name:"Protected Inputs",heading:"Sensitive inputs stay protected.",description:"Production plans and logistics records stay in separate environments."},
 {name:"Private Computation",heading:"Compute together. Keep control.",description:"A protected operation can produce reusable state. Disclosure is a separate decision."},
 {name:"Authorized Insights",heading:"Only the right insights come out.",description:"An explicit authorization boundary separates computation from permitted outputs."},
 {name:"Analytics Dashboard",heading:"From protected computation to clear decisions.",description:"Illustrative dashboard built from the same fixed sample summary."},
 {name:"Ask Your Authorized Data",heading:"Ask better questions. Reveal only what's permitted.",description:"Future concept on explicitly authorized summaries. The disclosure model remains to be defined."},
 {name:"From Insight to Action",heading:"One collaboration. Multiple possibilities.",description:"Possible applications of permitted insights, while protected state remains reusable."},
] as const;
export const businessDurations = [2600,2800,3200,3600,3800,4000,3600] as const;
export const sampleSummary = Object.freeze({deliveryGroupsAtRisk:3,onTimeRate:92,suppliersRequiringAttention:2});
