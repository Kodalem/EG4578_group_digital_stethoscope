```mermaid
graph TB

    W["Adaptive Scale Factor$$\text{: }\left\{\begin{array}{c}\text{If }|\Delta\tilde{\bf X}_{0}|\leq c_{0} \text{, then } \alpha_{\bf k}=1\\\text{If } c_{0}\leq|\Delta\tilde{\bf X}_{0}|\leq c,| \text{, then } \alpha_{\bf k}={\frac{c_{0}}{|\Delta\tilde{\mathrm{X}}_{\mathrm{k}}|}}\left({\frac{c_{1}-|\Delta\tilde{\mathrm{X}}_{\mathrm{k}}|}{|\Delta\tilde{\mathrm{X}}_{\mathrm{k}}|}}\right)\text{, where } \left|\Delta\tilde X_{k}\right|={\frac{\left||v_{k}\right||}{\sqrt{C_{v k}}}} \text{ of } C_{v k}=H\hat{P_{k}}^{-}H^{\top}+R_{k}\\\text{If } |\Delta\tilde{X}_{1}|\geq c_{1} \text{, then } \alpha_{\bf k}=0\end{array}\right. $$"]
    U["New Process Noise Info $$\text{: }\left\{\begin{array}{c}{{\hat{\mathrm{R}}_{\bf k+1}=(1-\mathrm{d}_{\bf k})\hat{\mathrm{R}}_{\bf k}+\mathrm{d}_{\bf k}(v_{\bf k}v_{\bf k}^{\top}-\mathrm{H}\hat{\mathrm{P}}_{\bf k}\mathbf{H}^{\top})}}\\{\mathbf{v}_{k}\,=\,v_{k}\,-\,H{\hat{x}}_{k}-{\hat{r}}_{k}}\\{\hat{r}_{k}\,=\,(\,1\,-\,d_{k})\hat{r}_{k-1}\,+\,d_{k}\,(z_{k}-H\hat{x}_{k-1}^{-})}\end{array}\right.$$"]
    T["New Measurement Covarience Noise Info $$\text{: }\left\{\begin{array}{c}{{\hat{\mathrm{Q}}_{{\bf{k}}+{\bf{1}}}=(1-\mathrm{d}_{{\bf{k}}})\hat{\mathrm{Q}}_{{\bf{k}}}+\mathrm{d}_{{\bf{k}}}({\bf{K}}_{{\bf{k}}}v_{{\bf{k}}}v_{{\bf{k}}}^{\top}{\bf{K}}_{{\bf{k}}}^{\top}+\hat{\mathrm{P}}_{{\bf{k}}}-{\bf{F}}\hat{\mathrm{P}}_{{\bf{k}}}{\bf{F}}^{\top})}}\\{\hat{\mathbf{q}}_{\mathbf{k}+1}=(1-\mathbf{d}_{\mathbf{k}})\hat{\mathbf{q}}_{\mathbf{k}}+\mathbf{d}_{\mathbf{k}}(\mathbf{x}_{\mathbf{k}}-\mathbf{F}\hat{\mathbf{x}}_{\mathbf{k}})}\end{array}\right. $$"]
    Y["Amnestic Factor $$\text{: }d_{k}={\frac{(1-b)}{(1-b^{k+1})}}$$"]
    Y --> U
    U --> T


    subgraph Predict
    A("Predict State Estimate  $$\text{: }\hat{x}_{k} = F_{k-1}\hat{x}_{k-1}+\hat{r}_{k-1}$$") 
    B("Estimate Covariance  $$\text{: }\hat{P}_{k}=F_{k-1}\hat{P}_{k-1}F^{\top}+Q_{k-1}$$")
    U --> A
    end
    subgraph Update
    C["Innovation Residual $$\text{: }y_k = z_k - H_k\hat{x}_{k}$$"]
    D["Innovation Covarience  $$\text{: }S_k = H\widehat{P}_{k}^{-}H^{\top}\,+\,\widehat{R}_{k}$$"]
    E["Kalman gain  $$\text{: }K_{k}\,=\,\frac{1}{\alpha_{k}}\,\widehat{P}_{k}^{-}H^{\top}(\frac{1}{\alpha_{k}}S_k)^{-1}$$"]
    F["Update State Estimate  $$\text{: }\hat{P}_{k+1} = (I-K_kH)\hat{P}^{-}_k\alpha_{k}{}^{-1}(I-K_kH)^{\top}+K_kR_kK^{\top}$$"]
    G["Update Covarience  $$\text{: }\hat{\mathbf{x}}_{\mathbf{k}}=[\mathbf{F}^{\mathsf{T}}{\hat{\mathbf{p}}}_{\mathbf{k}}^{-}\mathbf{F}+\alpha_{\mathbf{k}}{\hat{\mathbf{p}}}_{\mathbf{k}}^{-}]^{-1}\times(\mathbf{F}^{\mathsf{T}}{\hat{\mathbf{p}}}_{\mathbf{k}}^{-}\mathbf{y}+\alpha_{\mathbf{k}}{\hat{\mathbf{p}}}_{\mathbf{k}}^{-}\mathbf{\hat{x}}_{\mathbf{k}}^{-})$$"]

    A --> W
    B --> W

    W --> E
    W --> G

    A --> C 

    C --> G

    B --> D
    D --> E
    E --> F
    B --> E

    E --> G
    B --> F

    end
    E --> T
    F --> T
    G --> T

```